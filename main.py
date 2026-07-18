from fastapi import FastAPI
from api import api_router

app = FastAPI(title="Url Shortener API")

app.include_router(api_router)

@app.get('/')
def root():
    return {"message": "Url Shortener API"}