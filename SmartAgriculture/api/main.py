from fastapi import FastAPI

app = FastAPI(title="Smart Agriculture API")

@app.get("/")
def read_root():
    return {"message": "Smart Agriculture API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}