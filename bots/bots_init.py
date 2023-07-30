from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.webhook.aiohttp_server import TokenBasedRequestHandler, setup_application
from aiohttp import web

from bots.handlers import init_handlers
from bots.settings import *

logger = logging.getLogger('bots')


class Webhook:
    """Класс для поднятия вебхука."""
    def __init__(self):
        storage = RedisStorage.from_url(
            REDIS_LOCATION,
            key_builder=DefaultKeyBuilder(with_bot_id=True)
        )
        self.dp = Dispatcher(storage=storage)
        init_handlers(self.dp)

    def run(self):
        web_app = web.Application()
        TokenBasedRequestHandler(
            dispatcher=self.dp,
            bot_settings=bots_settings,
        ).register(web_app, path=WEBHOOK_PATH)
        setup_application(web_app, self.dp)
        web.run_app(
            web_app,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT
        )

    def run_test_polling(self):
        bot = Bot(
            os.getenv('TG_BOT_TOKEN'),
            session=bots_settings['session'],
            parse_mode=bots_settings['parse_mode']
        )
        self.dp.run_polling(bot)


if __name__ == '__main__':
    logger.info('Bot started')
    Webhook().run_test_polling() if DEBUG else Webhook().run()
