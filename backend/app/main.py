from fastapi import FastAPI

app = FastAPI(title="Dating App Backend")


@app.on_event("startup")
async def startup_event():
    print("🚀 Server is starting up... Dating App Backend is live!")


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.post("/users")
def create_user(user: dict):
    """
    Accepts a JSON body with user info, e.g.:
    {
        "email": "test@example.com",
        "name": "Andrew",
        "password": "123456"
    }
    """
    print(f"📩 Received new user: {user}")
    return {"message": "User received", "user": user}
