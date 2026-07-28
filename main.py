from fastapi import FastAPI

from router.auth_router import router

app = FastAPI()

app.include_router(router)


@app.get("/")
def root():
    return {"message": "API is running"}
