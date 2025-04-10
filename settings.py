from typing import Annotated

from pydantic import AfterValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def is_valid_yandex_path(value: str):
    if value[-1] != "/":
        raise ValueError('Should end with "/"')
    return value


def is_valid_pdf_name_template(value: str):
    if "." in value:
        raise ValueError(
            "Do not add extension. Only file name. Bad: output.pdf Ok: output"
        )
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="settings.txt",
        env_file_encoding="utf-8",
    )

    docx_output_dir: str = Field(default="docx")
    output_dir: str = Field(default="pdf")
    libre_office_path: str
    yandex_token: str
    pdf_name_template: Annotated[str, AfterValidator(is_valid_pdf_name_template)]
    result_column_name: str = "Презентация"
    yandex_path: Annotated[str, AfterValidator(is_valid_yandex_path)] = Field(
        default="/"
    )


def get_settings():
    return Settings()
