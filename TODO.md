# TODO — NotebookLM-clone (RAG) prototype

Living list of known issues and planned work. Ordered roughly by priority within each section.
Bug numbers (#1–#17) refer to the original codebase audit.

---

## 🔧 In progress (current work)

- [ ] **ModelService + lifespan startup** (`#7`)
  - [ ] Create `app/services/model_service.py`: class `ModelService` owning `AutoTokenizer` + `AutoModel` (both loaded once in `__init__`); move the mean-pooling `embed_chunk` logic from `embedding_service.py` into it.
  - [ ] `main.py`: add `lifespan` (`@asynccontextmanager`), build `ModelService()` before `yield`, attach to `app.state.model_service`; pass `lifespan=lifespan` to `FastAPI()`.
  - [ ] `app/dependencies.py`: add `get_model_service(request: Request) -> ModelService` returning `request.app.state.model_service`.
  - [ ] Refactor `DocumentProcessor.__init__` to receive `model_service` (drop internal `AutoTokenizer`).
  - [ ] Refactor `LLMService.response(...)` to take `model_service` (drop per-request `AutoTokenizer.from_pretrained`).
  - [ ] Delete module-level `embedding_service = EmbeddingService(...)` from `document_processor.py` and `llm_service.py`, then delete `embedding_service.py`.
  - [ ] Verify: importing `main`/routers loads no HF weights (check logs); one init line at startup only.

- [ ] **Service/repository DI cleanup**
  - [ ] Repositories take `db` in `__init__`; remove `db` param from repo methods (`auth_repository.py`, `document_repository.py`, `vector_repository.py`).
  - [ ] Services ctor-inject repositories; remove `db` param from service methods.
  - [ ] Providers in `app/dependencies.py`: `get_user_repository`, `get_user_service`, `get_document_service` (compose `model_service` there once ready).
  - [ ] Rewire routers to `Depends(get_user_service)` etc.; delete module-level `repository = ...` / `service = ...` chains (incl. `llm_service = LLMService(...)` in `llm_router.py`).
  - [ ] `dependencies.get_current_user`: stop constructing `UserRepository()` per call; use the provider.

---

## 🔴 Critical bugs (before any demo)

- [ ] **`#1` `auth_services.register_user`**: `HTTPException(status_code=409, message=...)` ×2 (username, email) → invalid kwarg, raises `TypeError` when triggered. Change to `detail=`.
- [ ] **`#2` `auth_services.login_user`**: annotate as `OAuth2PasswordRequestForm` — the `LoginRequest` type doesn't exist; runtime survives only via py3.14 lazy annotations, mypy fails.
- [ ] **`#3` `users_router.about_me`**: returns raw ORM `User` with `response_model=None` → serialization 500 + password_hash leak. Add a pydantic `UserPublicResponse` (id, username, email, verified, date_added) and set `response_model=`.
- [ ] **`#4` `document_processor.process_embed_document`**: `vector_repository.create_vector(...)` is dedented out of `if document_type == "pdf"` → `NameError` for `.txt`/`.docx` uploads. Re-indent; either implement txt/docx chunking or narrow `SUPPORTED_FORMATS` in `document_services.py` to `["pdf"]`.
- [ ] **`#5` Alembic baseline broken**: initial migration `a1aae69b5042` is empty; `users`/`documents` never created via migrations; `bc88487053a5` alters a nonexistent table. Re-baseline/squash migrations, then delete the import-time `Base.metadata.create_all(bind=engine)` from `app/database.py`.
- [ ] **`#6` `alembic/env.py:69`**: debug `print(config.get_main_option("sqlachemy.url"))` — typo `sqlachemy` raises in online migration runs. Remove the print.
- [ ] **`#8` Event-loop blocking**: sync torch embedding runs inside async endpoints (`upload_document`, `ask_question`). After ModelService lands, wrap embedding calls in `asyncio.to_thread` / `run_in_executor`.

---

## 🔵 Async DB migration (`async_get_db` is prepared in `app/database.py`)

- [ ] Repositories: `await db.scalar(...)`, `db.execute` → `await`, `await db.commit()`.
- [ ] `dependencies.get_current_user`: use `AsyncSession = Depends(async_get_db)`.
- [ ] Routers: switch `Depends(get_db)` → `Depends(async_get_db)`.
- [ ] `main.py` lifespan shutdown: `await async_engine.dispose()` after `yield`.
- [ ] Keep sync `get_db` intact until the very end — it's the agreed fallback.

---

## 🟡 Moderate / design

- [ ] **`#13` Implement `delete_user` flow** (models are ready — `User.documents` now cascades): repo `delete_user(db.delete + commit)`; service must also unlink every user file from `storage/` first (DB cascades don't touch the filesystem); wire the `POST /user/delete_user` endpoint (currently `raise NotImplementedError`).
- [ ] **`#12` Schema defaults**: `LoginTokenResponse` / `RegisterRequest` fields typed `str` but `Field(default=None)` → make them `str` with no default or `Optional[str]`.
- [ ] `auth_router` exports `router` — rename to `auth_router` for consistency with the other routers.
- [ ] REST nits (optional): `upload_document`/`delete_document` as `POST` → consider `DELETE /documents/{id}` conventions.

---

## 🟢 Quality / tooling

- [ ] **`#14` mypy CI**: workflow runs `uv run mypy` with no args/config; add `[tool.mypy]` to `pyproject.toml` (target `app`, `main.py`) or fix the command. Delete empty leftover `.github/workflows/mypy.noyml`.
- [ ] Pre-existing ruff sweep: `ruff check --fix` repo-wide (I001 import sorts, `typing.List`→`list` in `vector_repository.py`, etc.) — all pre-date current work.
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
- [ ] **Cross-encoder reranker** (S–M): `sentence-transformers` `CrossEncoder` rescores top-10 before LLM context; dep already present.
- [ ] **Batch embedding** (S): encode all chunks in one batched call — expect ~5–10× faster ingestion; good README metric.
- [ ] **Multi-query retrieval** (M): LLM rewrites question into 2–3 sub-queries, retrieve+merge; entry-level agentic RAG.

### Ingestion & jobs
- [ ] **txt/md + URL sources** (M): plain-text chunker (proper fix for `#4`, instead of just narrowing `SUPPORTED_FORMATS`); URL source: fetch page → markdown → same pipeline.
- [ ] **Background ingestion** (M): return `202 Accepted`, process via FastAPI `BackgroundTasks`; add `documents.status` (`processing/ready/failed`); properly resolves `#8` (event-loop blocking).

### Platform & ops
- [ ] **`pydantic-settings` Settings module** (S): replaces scattered `os.getenv`; do BEFORE dockerizing.
- [ ] **Dockerization** (M): multi-stage Dockerfile (uv); compose with `db` + `app` + `ollama` service (init container pulls `llama3.2:1b`); healthchecks; `alembic upgrade head` as entrypoint — forcing function to fix `#5`.
- [ ] **Refresh tokens** (M): access+refresh pair, `POST /auth/refresh` (current JWT hard-dies after 30 min).
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

- [ ] Two dev PDFs in `storage/` are still tracked in git (`storage/` now ignored going forward). Untrack with `git rm --cached storage/...` when ready — do NOT commit that change without review.
- [ ] README.md intentionally left empty — user has drafts on another machine.
- [ ] Dev DB contains SHA-1 document hashes from before the sha256 fix — re-uploads won't dedupe against old rows (harmless in dev).

---

## ✅ Done (do not redo)

- Repo hygiene: stray tracked file `̈` removed; `storage/` added to `.gitignore`.
- Moderate bugs `#9` (password_hash unique + `date_added` default), `#10` (sha1→sha256), `#11` (`Generator[int]`→`Generator[dict]`), `#15` (prompt "termination" line removed).
- Models: `User.documents` cascade (`all, delete-orphan`); redundant `unique=False` dropped; unused `Boolean` (vector_model) / `torch` (vector_repository) imports removed.
- `app/database.py`: `async_engine`, `AsyncSessionLocal`, `async_get_db` added alongside the untouched sync fallback; verified live (`SELECT 1`) and ruff-clean.
