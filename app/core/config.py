import os
class Settings:
    JWT_ALG = os.getenv("JWT_ALG","HS256")
    JWT_SECRET = os.getenv("JWT_SECRET","change_me")
    JWT_PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH","/run/keys/jwtRS256.key")
    JWT_PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH","/run/keys/jwtRS256.key.pub")
    JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS","3600"))
    CLIENT_ID = os.getenv("CLIENT_ID","demo")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET","demo123")
settings = Settings()
