from aiogram import Bot
from aiogram.utils.token import TokenValidationError
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from bots_admin.models import BotConfig, Chat, Message, TelegramBot, TGUser


class TGTokenField(forms.CharField):

    def clean(self, data):
        data = super(TGTokenField, self).clean(data)
        try:
            Bot(data)
        except TokenValidationError:
            raise ValidationError('Бот не существует', code='invalid')
        return self.to_python(data)


class TelegramBotForm(ModelForm):
    token = TGTokenField(label='Токен')

    class Meta:
        model = TelegramBot
        fields = '__all__'


class BotConfigModelAdmin(admin.StackedInline):
    model = BotConfig
    fieldsets = [
        ('Настройки OpenAI', {
            'fields': [
                'openai_api_key',
            ],
        }),
        ('Настройки бота', {
            'fields': ['prompt', 'bot_send_messages'],
        })
    ]
    raw_id_fields = ['bot']
    can_delete = False


@admin.register(Chat)
class ChatModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'tg_id', 'created_at']
    raw_id_fields = ['user', 'bot']
    search_fields = ['tg_id']


@admin.register(Message)
class MessageModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'tg_id', 'type', 'sender_type', 'created_at']
    search_fields = ['tg_id']


@admin.register(TelegramBot)
class TelegramBotModelAdmin(admin.ModelAdmin):
    form = TelegramBotForm
    inlines = [BotConfigModelAdmin]


@admin.register(TGUser)
class TGUserModelAdmin(admin.ModelAdmin):
    list_display = ['tg_id', 'username', 'first_name', 'last_name',
                    'created_at']


admin.site.unregister(Group)
admin.site.unregister(User)
