from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    database_user: str
    database_port: int
    database_password: str
    database_name: str
    database_host: str
    api_key: str
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

settings = Settings()
if(__name__ == "__main__"):
    # Create an instance
    settings = Settings(database_user="admin")

    # Now you can access the values
    postgres_url = f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"
    print(postgres_url)