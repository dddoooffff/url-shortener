from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.database import engine, create
from routers.url_short import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск")
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router=router)

@app.get("/")
async def index():
    ...