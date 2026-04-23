from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upbit_access_key: str = ""
    upbit_secret_key: str = ""

    okx_api_key: str = ""
    okx_secret_key: str = ""
    okx_passphrase: str = ""

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    debug: bool = False
    db_path: str = "data/trading.db"
    redis_url: str = "redis://redis:6379"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
