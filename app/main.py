from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, content, generate
from .database import engine, Base
# Import models to ensure they are registered with Base
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sawtna API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(content.router)
app.include_router(generate.router)
@app.get("/")
def read_root():
    return {"message": "Welcome to Sawtna API", "version": "1.0.0"}