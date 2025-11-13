from fastapi import FastAPI

from app.api.routes import auth as auth_routes

app = FastAPI(title="Dating App Backend")

app.include_router(auth_routes.router)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
