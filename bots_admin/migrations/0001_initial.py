# Generated by Django 4.2.2 on 2023-07-30 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_id', models.BigIntegerField(db_index=True, unique=True, verbose_name='TG ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Чат',
                'verbose_name_plural': 'Чаты',
                'db_table': 'chats',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TelegramBot',
            fields=[
                ('token', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='Токен')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Телеграм бот',
                'verbose_name_plural': 'Телеграм боты',
                'db_table': 'tg_bots',
            },
        ),
        migrations.CreateModel(
            name='TGUser',
            fields=[
                ('tg_id', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='TG ID')),
                ('username', models.CharField(blank=True, max_length=255, null=True, verbose_name='Username')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'TG Пользователи',
                'db_table': 'tg_users',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_id', models.BigIntegerField(db_index=True, unique=True, verbose_name='TG ID')),
                ('type', models.CharField(choices=[('text', 'Текст'), ('voice', 'Голос')], default='text', max_length=10, verbose_name='Тип')),
                ('text', models.TextField(max_length=500, verbose_name='Текст')),
                ('sender_type', models.CharField(choices=[('user', 'Пользователь'), ('assistant', 'Ассистент')], default='user', max_length=10, verbose_name='Тип отправителя')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='bots_admin.chat', verbose_name='Чат')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
                'db_table': 'messages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='chat',
            name='bot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='bots_admin.telegrambot', verbose_name='Бот'),
        ),
        migrations.AddField(
            model_name='chat',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='bots_admin.tguser', verbose_name='Пользователь'),
        ),
        migrations.CreateModel(
            name='BotConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openai_api_key', models.CharField(default='EMPTY', max_length=255, verbose_name='API ключ OpenAI')),
                ('prompt', models.TextField(default='You are a helpful assistant', verbose_name='PROMPT')),
                ('bot_send_messages', models.BooleanField(default=True, verbose_name='Бот может отправлять сообщения')),
                ('bot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='configs', to='bots_admin.telegrambot', verbose_name='Бот')),
            ],
            options={
                'verbose_name': 'Настройки бота',
                'verbose_name_plural': 'Настройки ботов',
                'db_table': 'bots_configs',
            },
        ),
    ]
