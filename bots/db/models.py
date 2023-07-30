from sqlalchemy import (BigInteger, Boolean, Column, DateTime, event,
                        ForeignKey, func, String, Text, Time)
from sqlalchemy.orm import relationship

from bots.db.base import BaseTable


class TelegramBot(BaseTable):
    __tablename__ = 'tg_bots'

    token = Column(String(255), primary_key=True)
    name = Column(String(100), nullable=True)

    configs = relationship('BotConfig', uselist=False, back_populates='bot')
    chats = relationship('Chat', back_populates='bot')

    def __repr__(self):
        return f'Bot {self.name or self.token}'


class TGUser(BaseTable):
    __tablename__ = 'tg_users'

    tg_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    chats = relationship('Chat', back_populates='user')

    def __repr__(self):
        return f'User {self.tg_id}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'


class Chat(BaseTable):
    __tablename__ = 'chats'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(BigInteger, ForeignKey('tg_users.tg_id'))
    user = relationship('TGUser', uselist=False, back_populates='chats')
    bot_id = Column(String(255), ForeignKey('tg_bots.token'))
    bot = relationship('TelegramBot', uselist=False, back_populates='chats')
    messages = relationship('Message', back_populates='chat')

    def __repr__(self):
        return f'Chat {self.tg_id}'


class Message(BaseTable):
    __tablename__ = 'messages'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, index=True, nullable=False)
    type = Column(String(10), default='text')
    text = Column(Text(500), nullable=False)
    sender_type = Column(String(10), default='user')
    created_at = Column(DateTime, default=func.now())

    chat_id = Column(BigInteger, ForeignKey('chats.id'))
    chat = relationship('Chat', uselist=False, back_populates='messages')

    def __repr__(self):
        return f'Message {self.id}'

    @classmethod
    def validate(cls, mapper, connection, target):
        if target.type not in {'text', 'voice'}:
            raise ValueError('Incorrect value for field "type"')
        if target.sender_type not in {'user', 'assistant'}:
            raise ValueError('Incorrect value for field "sender_type"')


class BotConfig(BaseTable):
    __tablename__ = 'bots_configs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    openai_api_key = Column(String(255), default='EMPTY')
    prompt = Column(Text, default='You are a helpful assistant')
    send_bot_messages = Column(Boolean, default=True)

    bot_id = Column(String(255), ForeignKey('tg_bots.token'), unique=True)
    bot = relationship('TelegramBot', uselist=False, back_populates='configs')

    def __repr__(self):
        return f'Configs. Bot {self.bot_token}'


@event.listens_for(Message, 'before_insert')
def validate_message(mapper, connection, target):
    target.validate(mapper, connection, target)
