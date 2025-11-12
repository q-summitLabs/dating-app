from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL
from sqlalchemy.engine.url import make_url


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    database_host: Optional[str] = Field(default=None, alias="DATABASE_HOST")
    database_port: int = Field(default=5432, alias="DATABASE_PORT")
    database_name: Optional[str] = Field(default=None, alias="DATABASE_NAME")
    database_user: Optional[str] = Field(default=None, alias="DATABASE_USER")
    database_password: Optional[SecretStr] = Field(default=None, alias="DATABASE_PASSWORD")
    database_sslmode: Optional[str] = Field(default="require", alias="DATABASE_SSLMODE")

    jwt_secret_key: SecretStr = Field(default=SecretStr("change-me"), alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 7, alias="REFRESH_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

    @property
    def async_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        required = {
            "DATABASE_HOST": self.database_host,
            "DATABASE_NAME": self.database_name,
            "DATABASE_USER": self.database_user,
            "DATABASE_PASSWORD": self.database_password,
        }
        missing = [name for name, value in required.items() if value in (None, "")]
        if missing:
            missing_display = ", ".join(missing)
            raise ValueError(
                f"Missing database settings: {missing_display}. "
                "Provide a DATABASE_URL or individual DATABASE_* variables."
            )

        password = (
            self.database_password.get_secret_value()
            if isinstance(self.database_password, SecretStr)
            else self.database_password
        )

        url = URL.create(
            drivername="postgresql+asyncpg",
            username=self.database_user,
            password=password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )
        return url.render_as_string(hide_password=False)

    @property
    def sync_database_url(self) -> str:
        url = make_url(self.async_database_url)
        if url.drivername.endswith("+asyncpg"):
            url = url.set(drivername="postgresql+psycopg")
        elif url.drivername == "postgresql":
            url = url.set(drivername="postgresql+psycopg")
        return url.render_as_string(hide_password=False)


settings = Settings()
