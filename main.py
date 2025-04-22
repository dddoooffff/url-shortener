from fastapi import FastAPI
from contextlib import asynccontextmanager

import uvicorn
from database.database import engine, create
from routers.url_short import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create()
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router=router)

@app.get("/")
async def index():
    ...
    
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)