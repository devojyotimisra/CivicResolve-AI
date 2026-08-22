from datetime import timedelta
from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = getenv("SQLALCHEMY_DATABASE_URI")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(getenv("JWT_ACCESS_TOKEN_EXPIRES_DAYS")))
    JWT_SECRET_KEY = getenv("JWT_SECRET_KEY")

    COMMISSIONER_MAIL = getenv("COMMISSIONER_MAIL")
    COMMISSIONER_PASSWORD = getenv("COMMISSIONER_PASSWORD")
    COMMISSIONER_NAME = getenv("COMMISSIONER_NAME")

    FRONTEND_URL = getenv("FRONTEND_URL")

    GROQ_API_KEY = getenv("GROQ_API_KEY")
    GROQ_MODEL = getenv("GROQ_MODEL", "qwen/qwen3.6-27b")

    HOST = getenv("HOST")
    PORT = int(getenv("PORT"))
