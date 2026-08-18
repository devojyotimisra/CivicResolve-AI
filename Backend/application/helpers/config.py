from os import getenv
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = getenv("SQLALCHEMY_DATABASE_URI")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS")))
    JWT_SECRET_KEY = getenv("JWT_SECRET_KEY")

    COMMISSIONER_MAIL = getenv("COMMISSIONER_MAIL")
    COMMISSIONER_PASSWORD = getenv("COMMISSIONER_PASSWORD")
    COMMISSIONER_NAME = getenv("COMMISSIONER_NAME")
    COMMISSIONER_PINCODE = getenv("COMMISSIONER_PINCODE")
    COMMISSIONER_ADDRESS = getenv("COMMISSIONER_ADDRESS")

    FRONTEND_URL = getenv("FRONTEND_URL")

    GEMINI_API_KEY = getenv("GEMINI_API_KEY")
    GEMINI_MODEL = getenv("GEMINI_MODEL", "gemma-4-31b-it")

    HOST = getenv("HOST")
    PORT = int(getenv("PORT"))
