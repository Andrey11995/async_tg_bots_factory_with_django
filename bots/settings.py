import logging
import os

from aiogram.client.session.aiohttp import AiohttpSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv('POSTGRES_HOST')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')

engine = create_async_engine(
    f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}',
    future=True,
    echo=True
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    future=True
)

DEBUG = bool(int(os.getenv('DEBUG', 0)))
bots_settings = {'session': AiohttpSession(), 'parse_mode': 'HTML'}

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('WEBAPP_PORT')
WEBHOOK_PATH = '/bots/{bot_token}'

REDIS_LOCATION = os.environ.get('REDIS_LOCATION')


def with_session(method):
    async def wrapper(cls, session=None, *args, **kwargs):
        if session:
            return await method(cls, session, *args, **kwargs)
        async with async_session() as session:
            return await method(cls, session, *args, **kwargs)
    return wrapper
