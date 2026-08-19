from fastapi import FastAPI

from app.router.auth_router import router
from app.router.document_router import document_router
from app.router.users_router import user_router
from app.router.llm_router import llm_router

app = FastAPI()

app.include_router(router)
app.include_router(user_router)
app.include_router(document_router)
app.include_router(llm_router)


@app.get("/")
def root():
    return {"message": "API is running"}
