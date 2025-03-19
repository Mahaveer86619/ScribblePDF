# app/main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.routes import router as routes_router

# Initialize FastAPI app
app = FastAPI(title="ScribblePDF")

# Secret key for session middleware (should be set in env for production)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Include our routes
app.include_router(routes_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)
