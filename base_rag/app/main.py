from fastapi import FastAPI
import app.rag.apis as ragapis
import app.auth.apis as authapis
import uvicorn 

app = FastAPI()

app.include_router(ragapis.router)
app.include_router(authapis.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8005, reload=False)