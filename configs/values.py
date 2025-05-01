import os
from dotenv import load_dotenv

load_dotenv(os.path.dirname(__file__).replace('configs','.env'))
class Config:
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    MONGO_URI = os.environ['MONGO_URI']

config = Config()
