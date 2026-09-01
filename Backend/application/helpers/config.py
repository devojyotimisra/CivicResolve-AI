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
    GROQ_MODEL = getenv("GROQ_MODEL")

    GROQ_BACKUP_API_KEY = getenv("GROQ_BACKUP_API_KEY")
    GROQ_BACKUP_MODEL = getenv("GROQ_BACKUP_MODEL")

    FALLBACK_API_KEY = getenv("FALLBACK_API_KEY")
    FALLBACK_MODEL = getenv("FALLBACK_MODEL")
    FALLBACK_BASE_URL = getenv("FALLBACK_BASE_URL")

    HOST = getenv("HOST")
    PORT = int(getenv("PORT"))
