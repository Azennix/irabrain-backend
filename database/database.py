import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# =====================================================
# LOAD ENVIRONMENT
# =====================================================

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env", override=False)


# =====================================================
# DATABASE CONFIGURATION
# =====================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured."
    )


# =====================================================
# DATABASE ENGINE
# =====================================================

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


# =====================================================
# DATABASE SESSION
# =====================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# =====================================================
# BASE MODEL
# =====================================================

Base = declarative_base()