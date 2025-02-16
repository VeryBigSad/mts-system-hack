from pydantic import BaseModel, SecretStr


class BaseConfigsModel(BaseModel):
    IS_DEBUG: bool = False
    EXTERNAL_URL: str | None = None
    HF_TOKEN: SecretStr | None = None
    GIGACHAT_TOKEN: str | None = None
    GIGACHAT_USER_ID: str | None = None


class RedisConfigsModel(BaseModel):
    REDIS_URL: str


class DataBaseConfigsModel(BaseModel):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str


class SettingsModel(
    BaseConfigsModel,
    RedisConfigsModel,
    DataBaseConfigsModel,
):
    pass
