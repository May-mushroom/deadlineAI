from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Reads from backend/.env, then the repo-root .env, then real environment variables.
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"

    database_url: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    auth_enabled: bool = False

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/integrations/google/callback"
    google_webhook_token: str = ""  # shared secret echoed back by Google on every push notification
    oauth_state_secret: str = ""  # signs the OAuth `state`; a per-process random value is used if empty

    frontend_url: str = "http://localhost:5173"  # where the OAuth callback sends the browser afterwards
    public_base_url: str = ""  # public HTTPS URL of this backend (e.g. an ngrok URL); needed for webhooks

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
