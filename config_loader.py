from dataclasses import dataclass
from os import getenv

from environs import Env


@dataclass
class Bot:
    token: str


@dataclass
class DB:
    host: str
    db_name: str
    user: str
    password: str


@dataclass
class PayProvider:
    pay_provider: str


@dataclass
class Config:
    bot: Bot
    db: DB
    pay_provider: PayProvider


env = Env()
env.read_env()


def load_config():

    return Config(
        bot=Bot(token=getenv("BOT_TOKEN")),
        db=DB(
            host=getenv("DB_HOST"),
            db_name=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASS")
        ),
        pay_provider=PayProvider(pay_provider=getenv("PROVIDER_TOKEN"))
    )
