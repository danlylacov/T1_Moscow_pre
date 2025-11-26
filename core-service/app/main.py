import os

from fastapi import FastAPI

from app.routers import projects, pipelines
from app.database import Base, engine


app = FastAPI(
    title="Self-Deploy Core Service",
    description="Автоматизированный сервис для генерации и проверки CI/CD пайплайнов",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    # Создаём таблицы, если их ещё нет.
    # В проде лучше использовать Alembic миграции.
    # Для разработки можно пересоздать таблицы, установив DROP_TABLES=true
    drop_tables = os.getenv("DROP_TABLES", "false").lower() == "true"
    if drop_tables:
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(pipelines.router, prefix="/pipelines", tags=["pipelines"])


@app.get("/health", tags=["service"])
async def health_check() -> dict:
    return {"status": "ok"}



