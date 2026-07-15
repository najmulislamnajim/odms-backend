from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    
    DATABASE_URL: str
    SAP_DATABASE_URL: str = ""
    
    # --- SAP MSSQL (read-only) ---
    SAP_DB_HOST: str = ""
    SAP_DB_PORT: int = 1433
    SAP_DB_USER: str = ""
    SAP_DB_PASSWORD: str = ""
    SAP_DB_NAME: str = ""
    
    @property
    def async_database_url(self) -> str:
        """For App — asyncpg driver."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def sync_database_url(self) -> str:
        """For Alembic/sync — psycopg2 driver."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)



settings = Settings()