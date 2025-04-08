from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='settings.txt',
        env_file_encoding='utf-8',
    )

    output_dir: str = Field(default="pdf")
    yandex_token: str


settings = Settings(_cli_exit_on_error=False)
