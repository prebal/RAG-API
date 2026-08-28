# TODO — NotebookLM-clone (RAG) prototype

Living list of known issues and planned work. Ordered roughly by priority within each section.
Bug numbers (#1–#17) refer to the original codebase audit.

---

## 🔧 In progress (current work)

_(All 🔴 Critical bugs #1–#8 closed as of 2026-08-26 ✅. Next up: portfolio polish track (tests / dockerize / README) or pick a feature.)_

---

## 🔴 Critical bugs (before any demo)

- [x] **`#1` `auth_services.register_user`**: `HTTPException(..., message=)` → `detail=` — fixed by user, runtime-verified (dup register returns 409 + detail). ✅
- [x] **`#2` `auth_services.login_user`**: annotated `OAuth2PasswordRequestForm` + import added — fixed by user, verified. ✅
- [x] **`#3` `users_router.about_me`**: fixed by user — `UserPublicResponse` (id/username/email/verified/date_added) + `response_model=UserPublicResponse` + typed return. Runtime-verified: `GET /user/me` → 200 with exactly the 5 fields, no `password_hash`. ✅ (optional polish: add `model_config = ConfigDict(from_attributes=True)` so manual `UserPublicResponse.model_validate(orm_user)` also works outside FastAPI's response path, e.g. in tests)
- [~] **`#4` `document_processor.process_embed_document`**: crash fixed 2026-08-25 — `embedded_chunks = []` guard + pdf-only embed; txt/docx uploads succeed with no chunks (no more `NameError`). Still no real txt/docx chunking: either narrow `SUPPORTED_FORMATS` to `["pdf"]` or implement it per the Ingestion & jobs feature item.
- [x] **`#5` Alembic baseline broken** — FIXED 2026-08-26 (user-driven): broken revisions deleted and replaced with single baseline `667bbda13c38_initial_commit.py` (users/documents/vector_table/refresh_tokens + `CREATE EXTENSION IF NOT EXISTS vector` + refresh_tokens via env.py model registration); env.py getter→setter fixed; import-time `create_all` removed from `app/database.py` (migrations are now the single source of schema truth). Verified on wiped DB: `alembic upgrade head` is the sole head, `alembic_version=667bbda13c38`, all 4 tables + `vector` extension present; app boot + register/login live-tested ✅.
- [x] **`#6` `alembic/env.py:69`**: debug `print(config.get_main_option("sqlachemy.url"))` removed — fixed by user, verified. ✅
- [x] **`#8` Event-loop blocking**: fixed 2026-08-25 — upload path offloads pure-CPU `embed_pdf` via `asyncio.to_thread` then persists on the main thread (`persist_chunks`); ask path offloads `embed_chunk` similarly. Live-verified: during a 22-page PDF embed, `GET /` latency stayed ~1–13 ms and 12 chunks persisted. ✅

---

## 🔵 Async DB migration (shipped 2026-08-25 ✅)

- [x] Repositories: `await db.scalar(...)`, `db.execute` → `await`, `await db.commit()` (incl. the `await`/paren-precedence fix sites).
- [x] `dependencies.get_current_user`: async + awaits repo via `AsyncSession` provider.
- [x] Routers: switch `Depends(get_db)` → `Depends(async_get_db)` — done via the 4 repository providers in `dependencies.py`; `get_db` import removed from `dependencies.py`.
- [x] `main.py` lifespan shutdown: `await async_engine.dispose()` after `yield`.
- [x] Keep sync `get_db` intact — sync engine/session/`create_all` fallback retained in `app/database.py`.

---

## 🟡 Moderate / design

- [x] **`#13` Implement `delete_user` flow** — shipped 2026-08-25: password-confirmed `DELETE /user/delete_user` (REST verb upgrade); `UserService` gathers filepaths, cascades erase user/docs/vectors/refresh-rows, storage files unlinked with `FileNotFoundError` tolerance ONLY after commit; `dependencies.py` reordered so providers are defined before use (`Depends` resolves references at def-time) + duplicate forward-referencing `get_user_service` removed. Gauntlet: wrong-password → 401, correct → 200, psql zeros, stale access → 401. ✅
- [x] **`#12` Schema defaults**: both `LoginTokenResponse` and `RegisterRequest` now have clean required fields (`Field(max_length=…)`) — fixed by user, verified. ✅
- [x] `auth_router` exports `auth_router` instead of bare `router` (renamed by user; `main.py` imports + mounts it correctly). ✅
- [ ] REST nits (optional): `upload_document`/`delete_document` as `POST` → consider `DELETE /documents/{id}` conventions.

### 🧱 Code-scan additions (from audit 2026-08-26)
- [ ] **`storage_path` via Settings**: replace hardcoded `LOCAL_STORAGE_PATH = "storage/"` in `storage_service.py` with a Settings field (default `./storage`) — currently breaks if uvicorn runs from any other CWD, and will break inside Docker.
- [ ] **`delete_document` FileNotFoundError tolerance**: mirror the delete_user loop's `except FileNotFoundError: pass` in `DocumentService.remove_document` so deleting a doc whose file was manually removed doesn't 500.
- [ ] **Refresh `expires_at` DB enforcement**: `TokenRepository.find_active_token_by_hash` never consults `expires_at` (rotation leans only on the JWT claim). Add expiry check + optional periodic sweep of expired/revoked rows.

---

## 🟢 Quality / tooling

- [~] **`#14` mypy CI**: empty leftover `.github/workflows/mypy.noyml` deleted by user ✅. Remaining: workflow runs `uv run mypy` with no args/config; add `[tool.mypy]` to `pyproject.toml` (target `app`, `main.py`) or fix the command.
- [ ] Pre-existing ruff sweep: only style debt left — `typing.Dict`/`typing.List`→builtin generics (UP006/UP035 in `users_router`, `document_router`, `document_services`, `vector_repository`, `model_service`) + import sort in `vector_repository.py` (I001). Everything else lint-clean.
- [ ] No tests exist. Add pytest + a few round-trips: register/login; upload→embed (use `dependency_overrides[get_model_service]` with a dummy model); delete_document; delete_user. CI job optional.

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
- [ ] **txt/md + URL sources** (M): plain-text chunker (proper fix for `#4`, instead of just narrowing `SUPPORTED_FORMATS`); URL source: fetch page → markdown → same pipeline.
- [ ] **Background ingestion** (M): return `202 Accepted`, process via FastAPI `BackgroundTasks`; add `documents.status` (`processing/ready/failed`); properly resolves `#8` (event-loop blocking).

### Platform & ops
- [~] **`pydantic-settings` Settings module** (S): `app/settings.py` created, consumed by `get_llm_clients` ✅. Remaining: migrate leftover `os.getenv` callers (`app/database.py`, `jwt_tokens.py` SECRET_KEY/ALGO, `alembic/env.py`) onto `get_settings()` — do BEFORE dockerizing.
- [ ] **Dockerization** (M): multi-stage Dockerfile (uv); compose with `db` + `app` + `ollama` service (init container pulls `llama3.2:1b`); healthchecks; `alembic upgrade head` as entrypoint (baseline now live since `#5` is closed).
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
- [ ] README.md intentionally left empty — user has drafts on another machine.
- [x] Dev DB contained SHA-1 document hashes from before the sha256 fix — MOOT: dev DB wiped 2026-08-26 (no documents exist anymore).

---

## ✅ Done (do not redo)

- Repo hygiene: stray tracked file `̈` removed; `storage/` added to `.gitignore`.
- Moderate bugs `#9` (password_hash unique + `date_added` default), `#10` (sha1→sha256), `#11` (`Generator[int]`→`Generator[dict]`), `#15` (prompt "termination" line removed).
- Models: `User.documents` cascade (`all, delete-orphan`); redundant `unique=False` dropped; unused `Boolean` (vector_model) / `torch` (vector_repository) imports removed.
- `app/database.py`: `async_engine`, `AsyncSessionLocal`, `async_get_db` added alongside the untouched sync fallback; verified live (`SELECT 1`) and ruff-clean.
- settings module `app/settings.py` (pydantic-settings) created; `get_llm_clients` consumes it via `get_settings()`.
- Alembic baseline IFM: broken version tree replaced with single squashed `667bbda13c38_initial_commit.py` (2026-08-26) — extension + all four tables + cascades; `create_all` removed from `database.py`; wipe-regenerate verification & live app smoke passed.
- argon2 `verify_password` hardened (2026-08-25): `VerifyMismatchError` (wrong password) is now caught and returned `False` instead of exploding — fixes latent 500s across login/change-username/change-password/delete_user. `check_and_change_password`'s old try/except pattern simplified accordingly.
- Async DB migration (2026-08-25): whole stack on `AsyncSession` via `async_get_db` providers; lifespan disposes `async_engine`; sync fallback intact. Live gauntlet passed: register/login/me/upload/dup-422/delete(+cascade, file unlink)/refresh-rotation/reuse-401/logout-401/parallel logins; zero `never awaited` warnings under `PYTHONASYNCIODEBUG=1`. Bugs fixed en route: async-`__init__` leftovers, double-`await`, awaited `db.add`, un-awaited internal calls, `await`-vs-paren precedence on `.execute(...).scalars()/.all()` chains, sync `storage_service` call awaited by mistake.
- `#8` fix (2026-08-25): CPU embedding split (`embed_pdf` offloaded to thread pool via `asyncio.to_thread`, `persist_chunks` on main thread) + question-embed offload; `#4` crash neutralized as side effect; `docment_to_write` typo + unbound guard bug fixed in `document_services.py`.
- Refresh tokens milestone (2026-08-25): stateful rotation + revocation shipped — `RefreshToken` model (sha256 hash, valid flag, expires_at), `TokenRepository`, service login/rotation/logout, `/auth/refresh` + `/auth/logout` routes, login ripple fix, confinement rule in `get_current_user`, `revoke_all_for_user` wired into `change_password`, `refresh_token_model.py` rename. Full live gauntlet passed. Optional flourish left: reuse-detection → mass-revoke on presented-revoked token.
- ModelService + DI refactor (2026-08-24): `app/services/model_service.py` (single tokenizer+model, lifespan-loaded via `app.state`); providers centralized in `app/dependencies.py` (`get_user/document/vector_repository`, `get_user/document_service`, `get_document_processor`, `get_model_service`, `get_current_user`); routers freed of module-level chains; `embedding_service.py` deleted; `app/settings.py` (pydantic-settings) + `get_llm_clients` (lru_cached clients) + per-request `get_llm_service` resolver (no sessions in the singleton) + `LLMRequest.provider` (local/api selector). E2E verified: boot, register/409/login, 503 guard for unconfigured `api` provider.
