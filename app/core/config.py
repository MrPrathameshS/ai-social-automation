import os
from dotenv import load_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)


class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

    # Security / Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Environment
    ENV: str = os.getenv("ENV", "development")

    # 🔵 LinkedIn OAuth (used only for auth flow)
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET")
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI")

    # 🟢 LinkedIn Publishing (USED BY publish_to_linkedin)
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN")
    LINKEDIN_AUTHOR_URN: str = os.getenv("LINKEDIN_AUTHOR_URN")



settings = Settings()


# =========================
# Debug checks (safe)
# =========================
print("🔥 CONFIG LOAD CHECK:", settings.GROQ_API_KEY)
print("🔥 DB URL CHECK:", settings.DATABASE_URL)
print("🔥 ENV CHECK:", settings.ENV)
