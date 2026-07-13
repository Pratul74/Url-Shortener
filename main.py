from fastapi import FastAPI

app = FastAPI(title="Url Shortener API")

@app.get('/')
def root():
    return {"message": "Url Shortener API"}