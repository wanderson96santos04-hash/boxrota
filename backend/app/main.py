from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes.public import router as public_router
from app.core.errors import add_exception_handlers
from app.core.settings import settings

app = FastAPI(title=settings.APP_NAME)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app)
app.include_router(api_router)
app.include_router(public_router)


@app.get("/health")
def health():
    return {"ok": True, "name": settings.APP_NAME}