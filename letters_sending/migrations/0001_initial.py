# Generated by Django 4.2.13 on 2024-08-13 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import libs.truncate_table_mixin


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Почта')),
                ('surname', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('name', models.CharField(max_length=100, verbose_name='Имя')),
                ('patronym', models.CharField(blank=True, max_length=100, null=True, verbose_name='Отчество')),
                ('comment', models.CharField(blank=True, max_length=255, null=True, verbose_name='Комментарий')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clients', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'клиенты',
                'ordering': ('surname', 'name', 'patronym', 'email'),
                'permissions': [('view_owner_client', 'Показать своих клиентов')],
            },
            bases=(libs.truncate_table_mixin.TruncateTableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DatePeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название')),
                ('description', models.CharField(max_length=100, verbose_name='Описание')),
                ('interval', models.PositiveIntegerField(verbose_name='Интервал (в секундах)')),
            ],
            options={
                'verbose_name': 'Интервал рассылки',
                'verbose_name_plural': 'интервалы рассылки',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='Название')),
                ('description', models.CharField(max_length=100, verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Статус рассылки',
                'verbose_name_plural': 'статусы рассылки',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('content', models.TextField(verbose_name='Содержание')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'сообщения',
                'ordering': ('subject',),
                'permissions': [('view_owner_message', 'Показать свои сообщения')],
            },
            bases=(libs.truncate_table_mixin.TruncateTableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='LettersSending',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_sending', models.DateTimeField(blank=True, null=True, verbose_name='Дата и время первой отправки')),
                ('next_sending', models.DateTimeField(blank=True, null=True, verbose_name='Дата и время следующей отправки')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность')),
                ('clients', models.ManyToManyField(to='letters_sending.client', verbose_name='Клиенты')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message', to='letters_sending.message', verbose_name='Сообщение')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sendings', to=settings.AUTH_USER_MODEL, verbose_name='автор')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='newsletter_period', to='letters_sending.dateperiod', verbose_name='Интервал')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='newsletter_status', to='letters_sending.status', verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Почтовая рассылка',
                'verbose_name_plural': 'почтовые рассылки',
                'permissions': [('deactivate_letterssending', 'Выключить рассылку'), ('view_owner_letterssending', 'Показать свои рассылки'), ('view_owner_stat_letterssending', 'Показать статистику своих рассылок'), ('view_stat_letterssending', 'Показать статистику рассылок')],
            },
            bases=(libs.truncate_table_mixin.TruncateTableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Attempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время')),
                ('is_sent', models.BooleanField(verbose_name='Отправлен')),
                ('response', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ответ сервера')),
                ('letters_sending', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='letters_sending', to='letters_sending.letterssending', verbose_name='Рассылка')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to='letters_sending.client', verbose_name='Получатель')),
            ],
            options={
                'verbose_name': 'Попытка отправки',
                'verbose_name_plural': 'попытки отправки',
                'ordering': ('created_at', 'is_sent'),
            },
        ),
    ]
