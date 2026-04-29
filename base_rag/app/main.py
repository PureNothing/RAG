from fastapi import FastAPI
import apis
import uvicorn 

app = FastAPI()

app.include_router(apis.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8005, reload=False)