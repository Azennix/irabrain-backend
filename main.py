import os
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth_routes import router as auth_router
from api.feedback_routes import router as feedback_router
from api.response_feedback_routes import router as response_feedback_router
from api.brain_routes import router as brain_router
from api.guest_routes import router as guest_router
from api.note_routes import router as note_router
from api.project_routes import router as project_router
from api.goal_routes import router as goal_router
from api.task_routes import router as task_router
from api.decision_routes import router as decision_router
from api.notification_routes import router as notification_router
from api.payment_routes import router as payment_router

from middleware.request_size_limit import RequestSizeLimitMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(
    title="IRABRAIN API",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_body_size=20 * 1024 * 1024,
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "irabrain.com",
            "www.irabrain.com",
        ],
    )
else:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            "192.168.1.101",
            "testserver",
        ],
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.101:3000",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
)
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    return response

app.include_router(auth_router)
app.include_router(feedback_router)
app.include_router(response_feedback_router)
app.include_router(brain_router)
app.include_router(guest_router)
app.include_router(note_router)
app.include_router(project_router)
app.include_router(goal_router)
app.include_router(task_router)
app.include_router(decision_router)
app.include_router(notification_router)
app.include_router(payment_router)


@app.get("/health")
def health():

    return {
        "status": "ok"
    }