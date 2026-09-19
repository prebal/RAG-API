# TODO — NotebookLM-clone (RAG) prototype

Living list of known issues and planned work. Ordered roughly by priority within each section.
Bug numbers (#1–#17) refer to the original codebase audit.

---

## 🔧 In progress (current work)

_(🔴 Critical bugs #1–#8 all closed; Docker stack committed & healthy; txt upload verified live; alembic+pgvector binding fixed; auth tests landed (11 ✓). Next: remaining test coverage sweep (documents/llm/delete trio), docx implementation choice per plan, occasional mypy re-decision, pyproject-features backlog at will.)_

---

## 🔴 Critical bugs (before any demo)

- [x] **`#1` `auth_services.register_user`**: `HTTPException(..., message=)` → `detail=` — fixed by user, runtime-verified (dup register returns 409 + detail). ✅
- [x] **`#2` `auth_services.login_user`**: annotated `OAuth2PasswordRequestForm` + import added — fixed by user, verified. ✅
- [x] **`#3` `users_router.about_me`**: fixed by user — `UserPublicResponse` (id/username/email/verified/date_added) + `response_model=UserPublicResponse` + typed return. Runtime-verified: `GET /user/me` → 200 with exactly the 5 fields, no `password_hash`. ✅ (optional polish: add `model_config = ConfigDict(from_attributes=True)` so manual `UserPublicResponse.model_validate(orm_user)` also works outside FastAPI's response path, e.g. in tests)
- [x] **`#4` `document_processor.process_embed_document`** — done (`7448ad3`): `chunk_tokenize_txt` mirrors the proven fixed-token-window pattern (256 tok / 30 overlap, line-numbered provenance via `line_buffer`); `embed_document` dispatches `document_type == "txt"` to real txt chunking; txt upload verified live. docx remains intentionally-future (see Ingestion & jobs).
- [x] **`#5` Alembic baseline broken** — FIXED 2026-08-26 (user-driven): broken revisions deleted and replaced with single baseline `667bbda13c38_initial_commit.py` (users/documents/vector_table/refresh_tokens + `CREATE EXTENSION IF NOT EXISTS vector` + refresh_tokens via env.py model registration); env.py getter→setter fixed; import-time `create_all` removed from `app/database.py` (migrations are now the single source of schema truth). Verified on wiped DB: `alembic upgrade head` is the sole head, `alembic_version=667bbda13c38`, all 4 tables + `vector` extension present; app boot + register/login live-tested ✅.
- [x] **`#6` `alembic/env.py:69`**: debug `print(config.get_main_option("sqlachemy.url"))` removed — fixed by user, verified. ✅
- [x] **`#8` Event-loop blocking**: fixed 2026-08-25 — upload path offloads pure-CPU `embed_pdf` via `asyncio.to_thread` then persists on the main thread (`persist_chunks`); ask path offloads `embed_chunk` similarly. Live-verified: during a 22-page PDF embed, `GET /` latency stayed ~1–13 ms and 12 chunks persisted. ✅

---

## 🔵 Async DB migration (shipped 2026-08-25 ✅)

- [x] Repositories: `await db.scalar(...)`, `db.execute` → `await`, `await db.commit()` (incl. the `await`/paren-precedence fix sites).
- [x] `dependencies.get_current_user`: async + awaits repo via `AsyncSession` provider.
- [x] Routers: switch `Depends(get_db)` → `Depends(async_get_db)` — done via the 4 repository providers in `dependencies.py`; `get_db` import removed from `dependencies.py`.
- [x] `main.py` lifespan shutdown: `await async_engine.dispose()` after `yield`.
- [x] Keep sync `get_db` intact — sync engine/session fallback retained in `app/database.py`; DDL now exclusively via alembic (import-time `create_all` removed with `#5`).

---

## 🟡 Moderate / design

- [x] **`#13` Implement `delete_user` flow** — shipped 2026-08-25: password-confirmed `DELETE /user/delete_user` (REST verb upgrade); `UserService` gathers filepaths, cascades erase user/docs/vectors/refresh-rows, storage files unlinked with `FileNotFoundError` tolerance ONLY after commit; `dependencies.py` reordered so providers are defined before use (`Depends` resolves references at def-time) + duplicate forward-referencing `get_user_service` removed. Gauntlet: wrong-password → 401, correct → 200, psql zeros, stale access → 401. ✅
- [x] **`#12` Schema defaults**: both `LoginTokenResponse` and `RegisterRequest` now have clean required fields (`Field(max_length=…)`) — fixed by user, verified. ✅
- [x] `auth_router` exports `auth_router` instead of bare `router` (renamed by user; `main.py` imports + mounts it correctly). ✅
- [~] REST nits: `delete_document` moved to proper `DELETE /delete_document/{document_id}` via path param (`9ca5946`); `upload_document` still `POST` (optional later).

### 🧱 Code-scan additions (from audit 2026-08-26)
- [x] **`storage_path` via Settings** — done: `storage_service` uses `settings.storage` (absolute via `PROJECT_ROOT_DIR` anchor; CWD-independent; docker-compose `/app/storage` volume supported via `STORAGE` env var).
- [x] **`delete_document` FileNotFoundError tolerance** — landed (`35edfa0`): `storage_service.py` wraps `os.remove` in `except FileNotFoundError: pass`; deleting a doc whose file was manually removed no longer 500s.
- [ ] **Refresh `expires_at` DB enforcement**: `TokenRepository.find_active_token_by_hash` never consults `expires_at` (rotation leans only on the JWT claim). Add expiry check + optional periodic sweep of expired/revoked rows.
- [x] **Small defect from strict-fill** — gone after the typing round (`9ca5946`): current ruff reports **`F821 = 0`** on `document_processor.py`; residual style debt (UP006/UP035, UP007) is tracked by the Quality sweep bullet.
- [x] **`Ollama healthcheck probe`** — fixed by user via the exact remediation: `["CMD-SHELL", "ollama list | grep -q $$LLM_LOCAL_MODEL"]` ✓ (`docker-compose.yml:33`).

---

## 🟢 Quality / tooling

- [~] **`#14` mypy CI**: `.github/workflows/mypy.noyml` deleted ✅; `[tool.mypy]` config landed (`python_version = "3.14"`, `files = ["main.py"]`) ✅; workflow now passes a target (`uv run mypy main.py`) ✅. Remaining: green-out the current 10 errors in 5 files (users_router ORM-return idiom, doc_processor `Dict` unimported annotation, strict-fill leftovers, aiofiles/pymupdf4llm stubs; widen `files` to include `app` matching the CI target).
- [~] Pre-existing ruff sweep (re-enumerated 2026-09 lingo): 74 findings — B008 ×35 (CI-ignored by design), **F821 ✓ 0**, UP006 ×13, UP035 ×10 (legacy `typing.Dict`/`List`), I001 ×8, F401 ×5, UP007 ×3 (`typing.Union`/`Optional` leftovers in alembic version file template lines).
- [~] Tests v1 landed partially (`d0d621f`): 11 `def test_*` covering register(+2 dupes), login + bad username + bad password, `/user/me`, change_username (+identical), change_password (+identical). Still uncovered: refresh-rotation trio + logout, `/user/me` confinement with refresh-as-bearer, documents upload→embed, delete_document, delete_user, and a CI tests workflow `.github/workflows/tests.yml` (not present).
- [x] **pyproject metadata** — done 2026-08-29: `name = "notebooklm-rag"`; description completed to a full sentence describing the RAG backend.

---

## ⚪ Performance / polish (later)

- [ ] ANN index on `vector_table.embedding` (HNSW via pgvector) once row counts grow; cosine queries currently seq-scan.
- [ ] `DateTime(timezone=True)` on timestamp columns (currently naive PG timestamps fed by aware `datetime.now(UTC)`).
- [ ] Optional: switch embedding to `SentenceTransformer(...).encode()` (sentence-transformers already a dep) — note: produces normalized vectors; cosine ranking unaffected but a re-embed of existing docs is cleaner.

---

## 🌟 Feature ideas (new functionality)

### NotebookLM core
- [ ] **Notebooks** (M): new `Notebook` model (`users → notebooks → documents`, FK on `documents`); scope Q&A per notebook via `.where(Document.notebook_id == ...)` in `select_k_best_chunks`; `/notebooks` CRUD router.
- [ ] **Grounded citations** (S): reuse stored `page_start`/`page_end` + document link; stream a `sources` SSE event before tokens; prompt LLM to cite `[1]` inline.
- [ ] **Abstention threshold** (S): use cosine `distance` from `select_k_best_chunks`; best distance > cutoff → answer "I don't know" instead of forcing garbage context.
- [ ] **Per-source summaries** (M): after embedding succeeds, one Ollama call → `documents.summary` column; NotebookLM-style Source Guide.
- [ ] **Selected-sources Q&A** (S): filter vector query by `document_id` list from request body.

### Retrieval depth
- [ ] **Hybrid search** (M): Postgres `tsvector` keyword search fused with pgvector results (RRF merge, ~40 lines, no new infra).
- [x] **Cross-encoder reranker** (S–M) — implemented 2026-08-26: `ModelService.cross_encoder` (ms-marco-MiniLM-L-6-v2, lifespan-loaded); `LLMService` widens retrieval to top-10, offloaded `.rank()` → top-5, context from `["text"]` entries; static-verified. Smoke test pending (requires Ollama for true end-to-end).
- [ ] **Batch embedding** (S): encode all chunks in one batched call — expect ~5–10× faster ingestion; good README metric.
- [ ] **Multi-query retrieval** (M): LLM rewrites question into 2–3 sub-queries, retrieve+merge; entry-level agentic RAG.

### Ingestion & jobs
- [~] **txt/md + URL sources** (M): txt chunker SHIPPED (`7448ad3` — proper fixed-token implementation after pdf's pattern, see `#4`); remaining: `docx`-parse support (still silent no-op against `SUPPORTED_FORMATS`), `.md` acceptance, `URL → markdown` ingestion source into the same pipeline.
- [ ] **Background ingestion** (M): return `202 Accepted`, process via FastAPI `BackgroundTasks`; add `documents.status` (`processing/ready/failed`); properly resolves `#8` (event-loop blocking).

### Platform & ops
- [x] **Settings migration** — complete as of 2026-08-29: `database.py`, `alembic/env.py`, and `jwt_tokens.py` all consume `get_settings()` (SECRET_KEY/ALGO sourced from the Settings object; `database_url` composed via env parts). Minor: `jwt_tokens.py` still keeps a now-unused `import os` (F401-sweep candidate).
- [x] **Dockerization** (M) — committed via `1640fba` "containerization should work": db + ollama (pull-entrypoint) + app (alembic+uvicorn entrypoint), healthchecked deps, 4 named volumes, `.dockerignore`, ollama env unified to `LLM_LOCAL_MODEL`. All packaging sealed (working tree clean) — leftovers shrink to: app-side health endpoint + uv/ollama image version pins.
- [x] **Refresh tokens** (M): access+refresh pair, `POST /auth/refresh` — **done 2026-08-25**, see 🔧 section for full status.
- [ ] **Health & observability** (S–M): `/health` probing DB + Ollama; structured logging with request IDs; optional `/metrics`.

### Stretch
- [ ] **Conversation memory per notebook** (M): `conversations`/`messages` tables → follow-up questions work.
- [ ] **Audio Overview** (L, stretch): LLM two-voice podcast script from sources + local TTS (piper) — fully offline.

### Suggested feature sequencing (after cleanup + critical bugs)
1. Settings → Notebooks → citations + abstention (+ summaries)   # notebook schema unlocks the rest
2. Background ingestion → txt/URL sources → batch embedding
3. Pick ONE retrieval-depth item (hybrid search recommended) for the "advanced RAG" story
4. Dockerize (with `#5` migration fix) → tests → health/metrics → refresh tokens
5. Stretch items last

---

## 📌 Decisions pending (user)

- [x] `smoketest_user`/`gauntlet_*` test accounts + gauntlet refresh-token rows — MOOT as of 2026-08-26: dev DB was wiped and regenerated via `alembic upgrade head` (all test data gone). Fresh dev DB now contains only newly created users (e.g., `wipetst_*`).

- [x] Two dev PDFs in `storage/` untracked (staged D by user) — commit to seal. `storage/` already ignored going forward via `.gitignore`.
- [x] README.md — first complete draft written 2026-08-29 (assistant-authored per user direction): title, badges, standouts, mermaid logic diagram, quickstart, auth model, RAG pipeline, API surface, config, dev status, roadmap. Pending: user's voice polish + demo GIF (placeholder slot reserved).
- [x] Dev DB contained SHA-1 document hashes from before the sha256 fix — MOOT: dev DB wiped 2026-08-26 (no documents exist anymore).

---

## ✅ Done (do not redo)

- Repo hygiene: stray tracked file `̈` removed; `storage/` added to `.gitignore`.
- Moderate bugs `#9` (password_hash unique + `date_added` default), `#10` (sha1→sha256), `#11` (`Generator[int]`→`Generator[dict]`), `#15` (prompt "termination" line removed).
- Models: `User.documents` cascade (`all, delete-orphan`); redundant `unique=False` dropped; unused `Boolean` (vector_model) / `torch` (vector_repository) imports removed.
- `app/database.py`: `async_engine`, `AsyncSessionLocal`, `async_get_db` added alongside the untouched sync fallback; verified live (`SELECT 1`) and ruff-clean.
- settings module `app/settings.py` (pydantic-settings) created; `get_llm_clients` consumes it via `get_settings()`.
- Alembic baseline IFM: broken version tree replaced with single squashed `667bbda13c38_initial_commit.py` (2026-08-26) — extension + all four tables + cascades; `create_all` removed from `database.py`; wipe-regenerate verification & live app smoke passed.
- Alembic `pgvector` namespace binding fix (`19c2dc1`): version file now imports `pgvector.sqlalchemy` directly (self-sufficient), and `alembic/env.py` model-import block restored (User/Document/RefreshToken/VectorEntry) — `AttributeError: module 'pgvector' has no attribute 'sqlalchemy'` inside the containerized upgrade path fully closed.
- argon2 `verify_password` hardened (2026-08-25): `VerifyMismatchError` (wrong password) is now caught and returned `False` instead of exploding — fixes latent 500s across login/change-username/change-password/delete_user. `check_and_change_password`'s old try/except pattern simplified accordingly.
- Async DB migration (2026-08-25): whole stack on `AsyncSession` via `async_get_db` providers; lifespan disposes `async_engine`; sync fallback intact. Live gauntlet passed: register/login/me/upload/dup-422/delete(+cascade, file unlink)/refresh-rotation/reuse-401/logout-401/parallel logins; zero `never awaited` warnings under `PYTHONASYNCIODEBUG=1`. Bugs fixed en route: async-`__init__` leftovers, double-`await`, awaited `db.add`, un-awaited internal calls, `await`-vs-paren precedence on `.execute(...).scalars()/.all()` chains, sync `storage_service` call awaited by mistake.
- `#8` fix (2026-08-25): CPU embedding split (`embed_pdf` offloaded to thread pool via `asyncio.to_thread`, `persist_chunks` on main thread) + question-embed offload; `#4` crash neutralized as side effect; `docment_to_write` typo + unbound guard bug fixed in `document_services.py`.
- Docker stack containerization (2026-08-29): db+ollama+app services with entrypoint `alembic upgrade head` + uvicorn host-flags, healthchecked dependencies, four named volumes; ollama env var unified to `LLM_LOCAL_MODEL`; in-container operation proven (compose-up demo).
- Refresh tokens milestone (2026-08-25): stateful rotation + revocation shipped — `RefreshToken` model (sha256 hash, valid flag, expires_at), `TokenRepository`, service login/rotation/logout, `/auth/refresh` + `/auth/logout` routes, login ripple fix, confinement rule in `get_current_user`, `revoke_all_for_user` wired into `change_password`, `refresh_token_model.py` rename. Full live gauntlet passed. Optional flourish left: reuse-detection → mass-revoke on presented-revoked token.
- ModelService + DI refactor (2026-08-24): `app/services/model_service.py` (single tokenizer+model, lifespan-loaded via `app.state`); providers centralized in `app/dependencies.py` (`get_user/document/vector_repository`, `get_user/document_service`, `get_document_processor`, `get_model_service`, `get_current_user`); routers freed of module-level chains; `embedding_service.py` deleted; `app/settings.py` (pydantic-settings) + `get_llm_clients` (lru_cached clients) + per-request `get_llm_service` resolver (no sessions in the singleton) + `LLMRequest.provider` (local/api selector). E2E verified: boot, register/409/login, 503 guard for unconfigured `api` provider.
