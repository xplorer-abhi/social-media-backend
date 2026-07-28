from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Social Media Backend Running"}