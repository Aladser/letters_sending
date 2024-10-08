from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from authen.services import CustomLoginRequiredMixin
from letters_sending.apps import LetterConfig
from letters_sending.forms import ClientForm
from letters_sending.models import Client
from letters_sending.services.services import OwnerVerificationMixin, OwnerListVerificationMixin
from letters_sending.views.views import CACHED_INDEX_KEY
from libs.managed_cache import ManagedCache
from libs.managed_cache_mixin import ManagedCacheMixin
from libs.custom_formatter import CustomFormatter

CACHED_CLIENTS_KEY = 'view_client'
"""ключ хранилища ключей кэшей страницы списка клиентов"""


# СПИСОК КЛИЕНТОВ
class ClientListView(CustomLoginRequiredMixin, OwnerListVerificationMixin, PermissionRequiredMixin,
                     ManagedCacheMixin, ListView):
    app_name = LetterConfig.name
    permission_required = app_name + ".view_owner_client"
    list_permission = app_name + '.view_client'
    list_owner_permission = app_name + '.view_owner_client'

    model = Client
    template_name = "client/list.html"
    title = 'Cписок клиентов'
    extra_context = {
        'title': title,
        'header': title
    }
    cached_key = CACHED_CLIENTS_KEY


# СОЗДАТЬ КЛИЕНТА
class ClientCreateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "letters_sending.add_client"

    model = Client
    template_name = "form.html"
    form_class = ClientForm
    success_url = reverse_lazy('client_list')

    title = "добавить клиента"
    extra_context = {
        'title': title,
        'header': title.capitalize()
    }

    def form_valid(self, form):
        if form.is_valid():
            self.object = form.save()
            self.object.owner = self.request.user
            self.object.save()

            ManagedCache.clear_data(CACHED_INDEX_KEY)
            ManagedCache.clear_data(CACHED_CLIENTS_KEY)
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["required_fields"] = CustomFormatter.get_form_required_field_labels(context["form"])
        context['back_url'] = reverse_lazy('client_list')

        return context


# ОБНОВИТЬ КЛИЕНТА
class ClientUpdateView(CustomLoginRequiredMixin, PermissionRequiredMixin, OwnerVerificationMixin, UpdateView):
    permission_required = "letters_sending.change_client"

    model = Client
    template_name = "form.html"
    form_class = ClientForm
    success_url = reverse_lazy('client_list')

    title = 'Изменить клиента'
    extra_context = {
        'title': title,
        'header': title,
        'back_url': success_url
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["required_fields"] = CustomFormatter.get_form_required_field_labels(context["form"])
        ManagedCache.clear_data(CACHED_CLIENTS_KEY)

        return context


# УДАЛИТЬ  КЛИЕНТА
class ClientDeleteView(CustomLoginRequiredMixin, PermissionRequiredMixin, OwnerVerificationMixin, DeleteView):
    permission_required = "letters_sending.delete_client"

    model = Client
    template_name = "confirm_delete.html"
    success_url = reverse_lazy('client_list')

    title = "удаление клиента"
    extra_context = {
        'css_list': ("confirm_delete.css",),
        'title': title,
        'header': title,
        'back_url': success_url,
        'object_type_name': "клиента"
    }

    def form_valid(self, form):
        print('form_valid')
        if form.is_valid():
            ManagedCache.clear_data(CACHED_CLIENTS_KEY)
            return super().form_valid(form)
