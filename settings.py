from typing import Annotated
from pydantic import AfterValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def is_valid_yandex_path(value: str):
    if value[-1] != "/":
        raise ValueError("Should end with \"/\"")
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="settings.txt",
        env_file_encoding="utf-8",
    )

    output_dir: str = Field(default="pdf")
    libre_office_path: str
    yandex_token: str
    yandex_path: Annotated[str, AfterValidator(is_valid_yandex_path)] = Field(default="/")


def get_settings():
    return Settings()
