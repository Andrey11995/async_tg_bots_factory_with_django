import asyncio
import logging
import os

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand, MenuButtonCommands
from django.db import models
from django.dispatch import receiver

logger = logging.getLogger('django')


class MessageType(models.TextChoices):
    TEXT = 'text', 'Текст'
    VOICE = 'voice', 'Голос'


class SenderType(models.TextChoices):
    USER = 'user', 'Пользователь'
    ASSISTANT = 'assistant', 'Ассистент'


class FileType(models.TextChoices):
    IMAGE = 'image', 'Фото'
    VIDEO = 'video', 'Видео'
    AUDIO = 'audio', 'Аудио'


class TGBot:
    """Класс инициализации ботов."""
    WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
    WEBHOOK_PATH = '/bots/{bot_token}'
    WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

    def __init__(self, token):
        self.token = token
        self.bot = Bot(self.token)

    def start(self):
        asyncio.new_event_loop().run_until_complete(self.__start())

    def delete(self):
        asyncio.new_event_loop().run_until_complete(self.__delete())

    async def __start(self):
        async with AiohttpSession() as session:
            self.bot.session = session
            await self.bot.delete_webhook(drop_pending_updates=True)
            # закомментировать set_webhook при запуске бота в DEBUG режиме
            # await self.bot.set_webhook(
            #     self.WEBHOOK_URL.format(bot_token=self.token)
            # )
            await self.bot.set_my_commands([
                BotCommand(
                    command='start',
                    description='Запустить бота'
                )
            ])
            bot_menu_button = MenuButtonCommands(text='Меню')
            await self.bot.set_chat_menu_button(
                menu_button=bot_menu_button
            )
        logger.info(f'Bot {self.token} is running')

    async def __delete(self):
        async with AiohttpSession() as session:
            self.bot.session = session
            await self.bot.delete_webhook(drop_pending_updates=True)
        logger.info(f'Bot {self.token} deleted')


class TelegramBot(models.Model):
    token = models.CharField('Токен', max_length=255, primary_key=True)
    name = models.CharField('Название', max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'tg_bots'
        verbose_name = 'Телеграм бот'
        verbose_name_plural = 'Телеграм боты'

    def __str__(self):
        return self.name or f'Bot {self.token}'

    def start_bot(self):
        TGBot(self.token).start()

    def delete_bot(self):
        TGBot(self.token).delete()


class TGUser(models.Model):
    tg_id = models.BigIntegerField('TG ID', primary_key=True)
    username = models.CharField('Username', max_length=255,
                                null=True, blank=True)
    first_name = models.CharField('Имя', max_length=255, null=True, blank=True)
    last_name = models.CharField('Фамилия', max_length=255,
                                 null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        db_table = 'tg_users'
        ordering = ['-created_at']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'TG Пользователи'

    def __str__(self):
        return f'TGUser {self.tg_id}'


class Chat(models.Model):
    tg_id = models.BigIntegerField('TG ID', unique=True, db_index=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    user = models.ForeignKey(
        TGUser,
        on_delete=models.CASCADE,
        related_name='chats',
        verbose_name='Пользователь'
    )
    bot = models.ForeignKey(
        TelegramBot,
        on_delete=models.CASCADE,
        related_name='chats',
        verbose_name='Бот'
    )

    class Meta:
        db_table = 'chats'
        ordering = ['-created_at']
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f'Chat {self.tg_id}'


class Message(models.Model):
    tg_id = models.BigIntegerField('TG ID', unique=True, db_index=True)
    type = models.CharField(
        'Тип',
        max_length=10,
        choices=MessageType.choices,
        default=MessageType.TEXT
    )
    text = models.TextField('Текст', max_length=500)
    sender_type = models.CharField(
        'Тип отправителя',
        max_length=10,
        choices=SenderType.choices,
        default=SenderType.USER
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Чат'
    )

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'Message {self.tg_id}'


class BotConfig(models.Model):
    bot = models.OneToOneField(
        TelegramBot,
        on_delete=models.CASCADE,
        related_name='configs',
        verbose_name='Бот'
    )
    openai_api_key = models.CharField('API ключ OpenAI', max_length=255,
                                      default='EMPTY')
    prompt = models.TextField('PROMPT', default='You are a helpful assistant')
    bot_send_messages = models.BooleanField('Бот может отправлять сообщения',
                                            default=True)

    class Meta:
        db_table = 'bots_configs'
        verbose_name = 'Настройки бота'
        verbose_name_plural = 'Настройки ботов'

    def __str__(self):
        return f'Bot {self.bot.token}'


@receiver(models.signals.post_save, sender=TelegramBot)
def bot_start(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'configs'):
            BotConfig.objects.create(bot_id=instance.token)
        instance.start_bot()


@receiver(models.signals.pre_delete, sender=TelegramBot)
def bot_delete(sender, instance, **kwargs):
    instance.delete_bot()
