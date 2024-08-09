from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from authen.services import CustomLoginRequiredMixin, show_error
from letters_sending.apps import LetterConfig
from letters_sending.forms import LettersSendingCreateForm, LettersSendingUpdateForm
from letters_sending.models import LettersSending, Status
from letters_sending.services.send_letters import send_letters
from letters_sending.services.services import OwnerListVerificationMixin
from libs.custom_formatter import CustomFormatter

TEMPLATE_FOLDER = LetterConfig.name + '/'


# СПИСОК РАССЫЛОК
class LettersSendingListView(CustomLoginRequiredMixin, OwnerListVerificationMixin, PermissionRequiredMixin, ListView):
    app_name = LetterConfig.name
    permission_required = app_name + ".view_owner_letterssending"

    model = LettersSending
    template_name = TEMPLATE_FOLDER + "list.html"
    extra_context = {
        'title': '',
        'header': "Cписок рассылок",
        'css_list': ("letters_sending.css",)
    }

    def get(self, *args, **kwargs):
        if str(self.request.user) == 'AnonymousUser':
            return redirect(reverse('authen:login'))
        return super().get(*args, **kwargs)


# ДЕТАЛИ РАССЫЛКИ
class LettersSendingDetailView(CustomLoginRequiredMixin, DetailView):
    model = LettersSending

    def get_context_data(self, **kwargs):
        if not (self.request.user.has_perm(
                'letters_sending.view_letterssending') or self.object.owner == self.request.user):
            context = {'title': 'доступ запрещен', 'description': 'У вас нет доступа к этой рассылке'}
            self.template_name = "info.html"
        else:
            context = super().get_context_data(**kwargs)
            title = f"рассылка №{self.object.pk}"
            context['title'] = context['header'] = title
            self.template_name = TEMPLATE_FOLDER + "detail.html"

        return context


# СОЗДАТЬ РАССЫЛКУ
class LettersSendingCreateView(CustomLoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "letters_sending.add_letterssending"

    model = LettersSending
    template_name = "form.html"
    form_class = LettersSendingCreateForm
    title = "добавить рассылку"
    extra_context = {
        'title': title,
        'header': title
    }

    def form_valid(self, form):
        if form.is_valid:
            self.object = form.save()
            # установка даты первой отправки сообщений
            if self.object.status.name == "launched" and not self.object.first_sending:
                self.object.first_sending = datetime.now()
            self.object.next_sending = self.object.first_sending
            self.object.owner = self.request.user
            self.object.save()

            if self.object.status.name == "launched":
                # запуск задачи
                send_letters(self.object)
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["required_fields"] = CustomFormatter.get_form_required_field_labels(context["form"])
        context['back_url'] = reverse_lazy('letter_sending_list')

        return context

    def get_success_url(self):
        return reverse_lazy("letter_sending_detail", kwargs={"pk": self.object.pk})


# ОБНОВИТЬ РАССЫЛКУ
class LettersSendingUpdateView(CustomLoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "letters_sending.change_letterssending"

    model = LettersSending
    template_name = "form.html"
    form_class = LettersSendingUpdateForm

    def form_valid(self, form):
        if form.is_valid:
            self.object = form.save()
            if self.object.status.name == "launched":
                if not self.object.first_sending:
                    self.object.first_sending = datetime.now()
                if not self.object.next_sending:
                    self.object.next_sending = self.object.first_sending
                if self.object.next_sending <= datetime.now():
                    # если время запуска просрочено
                    send_letters(self.object)
            self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("letter_sending_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        title = f"изменить рассылку №{self.object.pk}"
        context['title'] = context['header'] = title
        context["required_fields"] = CustomFormatter.get_form_required_field_labels(context["form"])
        context['back_url'] = reverse_lazy("letter_sending_detail", kwargs={"pk": self.object.pk})

        return context


# УДАЛИТЬ РАССЫЛКУ
class LettersSendingDeleteView(CustomLoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "letters_sending.delete_letterssending"

    model = LettersSending
    template_name = "confirm_delete.html"
    success_url = reverse_lazy('letter_sending_list')
    extra_context = {
        'css_list': ("confirm_delete.css",),
        "type": "рассылку",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['header'] = f"удаление рассылки №{self.object.pk}"
        context['object_type_name'] = "рассылку"
        context['back_url'] = reverse_lazy("letter_sending_detail", kwargs={"pk": self.object.pk})

        return context


# ВЫКЛЮЧИТЬ АКТИВНУЮ РАССЫЛКУ
@login_required
@permission_required('letters_sending.deactivate_letterssending')
def deactivate_letterssending(request):
    """Выключить активную рассылку"""

    sending = LettersSending.objects.filter(pk=request.POST['pk'])
    if sending.exists():
        sending = sending.first()

        # если рассылка не запущена
        if sending.status.name == 'launched':
            sending.status = Status.objects.get(name='completed')
            sending.save()
            return redirect(reverse('letter_sending_detail', kwargs={'pk': sending.pk}))
        else:
            return show_error(request, f'Ошибка: рассылка не запущена')
    else:
        return show_error(request, f'Ошибка: рассылка не найдена')
