from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env',env_file_encoding="utf-8")
    
    DATABASE_URL:str
    JWT_SECRET:str
    JWT_ALGO:str='HS256'
    ACCES_TOKEN_EXPIRE_MINUTES:int=30

settings=Settings()