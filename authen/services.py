from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse_lazy
from django_redis import get_redis_connection

class CustomLoginRequiredMixin(LoginRequiredMixin):
    """Кастомизированный миксин обязательной авторизации"""

    login_url = reverse_lazy('authen:login')
    redirect_field_name = 'redirect_to'


def show_error(request, exception, status=None):
    """Выводит ошибку на страницу"""

    return render(request,'info.html',{'title': 'ошибка', 'description': exception})


def e_handler403(request, exception=None):
    """Выводит ошибку 403"""

    return render(request,
                  'info.html',
                  status=403,
                  context={'title': 'Доступ запрещен', 'description': f'Доступ запрещен\n {exception}'})


def get_cached_data(key, pk):
    """
    Получает данные из кэша
    :param key: ключ хранилища ключей страницы
    :param pk: pk пользователя
    """

    user_key = f'{key}_{pk}'
    key_store_list = cache.get(key)

    if key_store_list is None:
        cache.set(key, [])
        return None
    elif user_key in key_store_list:
        return cache.get(user_key)
    return None


def save_cached_data(key, pk, data):
    """
    Сохранят данные в кэше
    :param key: ключ хранилища ключей страницы
    :param pk: pk пользователя
    :param data: данные
    """

    user_key = f'{key}_{pk}'
    # обновляет хранилище ключей
    key_store_list = cache.get(key)
    key_store_list.append(user_key)
    cache.set(key, key_store_list)
    # сохраняем страницу пользователя
    cache.set(user_key, data)
