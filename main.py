from fastapi import FastAPI

from router.auth_router import router
from router.users_router import user_router

app = FastAPI()

app.include_router(router)
app.include_router(user_router)
app.include_router(document_router)


@app.get("/")
def root():
    return {"message": "API is running"}
