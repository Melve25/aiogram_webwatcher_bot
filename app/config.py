from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
	BOT_TOKEN: str
	DB_URL: str
	POSTGRES_USER: str
	POSTGRES_PASSWORD: str
	POSTGRES_DB: str
	DB_HOST: str
	DB_PORT: str

	model_config = SettingsConfigDict(env_file='.env')


settings = AppSettings()

