from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth as auth_routes,
    groups as groups_routes,
    matching as matching_routes,
    photos as photos_routes,
)

app = FastAPI(title="Dating App Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(groups_routes.router)
app.include_router(matching_routes.router)
app.include_router(photos_routes.router)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
