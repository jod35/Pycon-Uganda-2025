from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    DOMAIN_NAME : str

    model_config  = SettingsConfigDict(env_file='.env')


CONFIG = Settings()