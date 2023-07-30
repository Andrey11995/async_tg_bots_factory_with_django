import asyncio
import datetime as dt

from aiogram import Bot
from django.db.models import Max, Subquery

from bots_admin.models import Chat, Message, MessageType, SenderType
from bots_factory.celery import app

loop = asyncio.get_event_loop()


@app.task
def check_last_messages_time():
    """
    Выбирает чаты, в которых последнее сообщение было отправлено раньше,
    чем n часов назад.
    """
    n = 23
    delta = dt.datetime.now() - dt.timedelta(hours=n)
    chats = Chat.objects.filter(
        bot__configs__bot_send_messages=True,
        id__in=Subquery(
            Message.objects.filter(
                id__in=Subquery(
                    Message.objects.values('chat').annotate(
                        max_id=Max('id')
                    ).values('max_id')
                ),
                created_at__lt=delta
            ).values('chat')
        )
    ).distinct()
    for chat in chats:
        send_bot_message.apply_async([
            chat.bot.token,
            chat.id,
            chat.tg_id
        ])


@app.task
def send_bot_message(bot_token, chat_id, tg_id, message='Hello'):
    """Отправляет сообщения в выбранные чаты."""
    bot = Bot(bot_token)
    tg_message = loop.run_until_complete(bot.send_message(
        tg_id,
        message
    ))
    Message.objects.create(
        tg_id=tg_message.message_id,
        chat_id=chat_id,
        type=MessageType.TEXT,
        text=message,
        sender_type=SenderType.ASSISTANT
    )
