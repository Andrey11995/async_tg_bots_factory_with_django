import io
import logging
from tempfile import NamedTemporaryFile
from typing import Union

import openai
from aiogram import Bot
from aiogram.types import (Animation, Audio,
                           Document, PhotoSize, Sticker, Video,
                           VideoNote, Voice)
from pydub import AudioSegment

from bots.db.models import BotConfig

logger = logging.getLogger('bots')

TG_FILE = Union[
    Audio,
    Animation,
    Document,
    PhotoSize,
    Sticker,
    Video,
    VideoNote,
    Voice
]


def with_configs(method):
    async def wrapper(bot: Bot, *args, **kwargs):
        configs = await BotConfig.get(bot_id=bot.token)
        return await method(*args, **kwargs, configs=configs)
    return wrapper


@with_configs
async def request_to_gpt(message, configs: BotConfig):
    try:
        openai.api_key = configs.openai_api_key
        messages = [
            {
                'role': 'system',
                'content': configs.prompt
            },
            {
                'role': 'user',
                'content': message
            }
        ]
        response = await openai.ChatCompletion.acreate(
            model='gpt-3.5-turbo',
            messages=messages
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f'OpenAI error: {e}')
        return {
            'error': str(e),
            'answer': f'OpenAI error: {e}. Please try again later'
        }


@with_configs
async def get_voice_transcript(voice, configs):
    try:
        openai.api_key = configs.openai_api_key
        with NamedTemporaryFile(suffix='.ogg') as file:
            file.write(voice.getbuffer())
            file.flush()
            ogg_audio = AudioSegment.from_ogg(file.name)
        wav_audio = ogg_audio.export(format='wav')
        with NamedTemporaryFile(suffix='.wav') as file:
            file.write(wav_audio.read())
            file.flush()
            file.seek(0)
            transcript = await openai.Audio.atranscribe(
                file=file,
                model='whisper-1',
                headers={'Content-Type': 'audio/wav'}
            )
        return transcript.get('text')
    except Exception as e:
        logger.error(f'OpenAI transcript error: {e}')


async def download_file(bot: Bot, file: TG_FILE):
    output = io.BytesIO()
    file = await bot.get_file(file.file_id)
    return await bot.download_file(file.file_path, destination=output)
