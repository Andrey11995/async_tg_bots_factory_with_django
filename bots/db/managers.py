from bots.db.models import Chat, Message, TGUser


async def get_or_create_user(tg_user):
    return (await TGUser.get_or_create(
        tg_id=tg_user.id,
        defaults={
            'username': tg_user.username,
            'first_name': tg_user.first_name,
            'last_name': tg_user.last_name
        }
    ))[0]


async def get_or_create_chat(chat_id, user_id, bot):
    return (await Chat.get_or_create(
        tg_id=chat_id,
        bot_id=bot.token,
        defaults={
            'user_id': user_id,
        }
    ))[0]


async def create_message(message, by_user=True, message_type='text'):
    return await Message.create(
        tg_id=message['id'],
        type=message_type,
        text=message['text'],
        sender_type='user' if by_user else 'assistant',
        chat_id=message['chat']
    )
