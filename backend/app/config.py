from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = "mongodb://localhost:27017/codeax"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    github_webhook_secret: str = ""
    github_api_base_url: str = "https://api.github.com"
    github_app_id: str = ""
    github_private_key_path: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    github_token: str = "" # Fallback static token for testing 

    enable_auto_pr_comment: bool = True


settings = Settings()
