from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    instagram_username : str
    instagram_password : str
    email:str
    email_password:str

    class Config:
        env_file = ".env"

envset = Settings()
