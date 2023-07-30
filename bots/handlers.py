import io

from aiogram import Bot, F, types
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.types import FSInputFile

from bots.db.managers import *
from bots.utils import download_file, get_voice_transcript, request_to_gpt


def init_handlers(dp):
    @dp.message(Command(commands=['start']))
    async def cmd_start(message: types.Message, bot: Bot):
        """Обработчик команды /start."""
        user = await get_or_create_user(message.from_user)
        await get_or_create_chat(message.chat.id, user.tg_id, bot)
        await message.answer('Welcome!')
        await message.answer_photo(
            FSInputFile('./bots/bots_static/hello_photo.png')
        )

    @dp.message(
        F.content_type == ContentType.TEXT,
        F.text.func(lambda text: len(text) <= 500)
    )
    async def text_message(message: types.Message, bot: Bot):
        """Обработчик текстовых сообщений."""
        user = await get_or_create_user(message.from_user)
        chat = await get_or_create_chat(message.chat.id, user.tg_id, bot)
        await message.chat.do('typing')
        message_obj = await create_message(
            {
                'id': message.message_id,
                'text': message.text,
                'chat': chat.id
            }
        )
        response = await request_to_gpt(bot, message_obj.text)
        # Если ответ не получен, отправляем сообщение об ошибке
        if isinstance(response, dict) and 'error' in response:
            response = response['answer']
        bot_message = await message.answer(response)
        await create_message(
            {
                'id': bot_message.message_id,
                'text': bot_message.text,
                'chat': chat.id
            },
            by_user=False
        )

    @dp.message(
        F.content_type == ContentType.VOICE,
        F.voice.func(lambda voice: voice.duration < 60)
    )
    async def voice_message(message: types.Message, bot: Bot):
        """Обработчик голосовых сообщений."""
        user = await get_or_create_user(message.from_user)
        chat = await get_or_create_chat(message.chat.id, user.tg_id, bot)
        await message.chat.do('typing')
        file = await download_file(bot, message.voice)
        transcript = await get_voice_transcript(bot, file)
        if not transcript:
            await message.answer('Not understand')
            return
        message_obj = await create_message(
            {
                'id': message.message_id,
                'text': transcript,
                'chat': chat.id
            },
            message_type='voice'
        )
        response = await request_to_gpt(bot, message_obj.text)
        if isinstance(response, dict) and 'error' in response:
            response = response['answer']
        bot_message = await message.answer(response)
        await create_message(
            {
                'id': bot_message.message_id,
                'text': response,
                'chat': chat.id
            },
            by_user=False
        )

    @dp.message(F.content_type == ContentType.STICKER)
    async def sticker_message(message: types.Message):
        """Обработчик стикеров."""
        await message.answer(message.sticker.emoji)

    @dp.message(F.content_type == ContentType.DOCUMENT)
    async def document_message(message: types.Message):
        """Обработчик документов."""
        pass

    @dp.message(F.content_type == ContentType.ANIMATION)
    async def animation_message(message: types.Message):
        """Обработчик анимаций."""
        pass

    @dp.message(F.content_type == ContentType.PHOTO)
    async def photo_message(message: types.Message):
        """Обработчик фотографий."""
        pass

    @dp.message(F.content_type == ContentType.VIDEO)
    async def video_message(message: types.Message):
        """Обработчик видео."""
        pass

    @dp.message(F.content_type == ContentType.CONTACT)
    async def contact_message(message: types.Message):
        """Обработчик контактов."""
        pass
