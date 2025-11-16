import abc
import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Singleton(abc.ABCMeta, type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractSingleton(abc.ABC, metaclass=Singleton):
    pass


class Config(metaclass=Singleton):
    def __init__(self):
        """构建数据库连接 URL"""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "winwin")
        username = os.getenv("POSTGRES_USER", "winwin")
        password = os.getenv("POSTGRES_PASSWORD", "winwin1234")

        self.postgres_uri = f"postgresql://{username}:{password}@{host}:{port}/{database}"


cfg = Config()
