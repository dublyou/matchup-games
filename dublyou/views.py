# -*- coding: utf-8 -*-
from functools import partial
from functools import wraps
from copy import deepcopy

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.forms import ModelForm, modelformset_factory, inlineformset_factory, BaseModelFormSet, BaseInlineFormSet
from django.forms.formsets import BaseFormSet, formset_factory
from django.views.generic.edit import FormView, CreateView, UpdateView, FormMixin
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin, DetailView
from django.views.generic.base import View, ContextMixin, TemplateResponseMixin
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse, resolve
from django.db.models import QuerySet

from .forms import ContactForm
from .utils import get_attr_mult, send_notification


class ObjectPermissionsMixin(AccessMixin):
    permission_logic = None
    permissions = None
    permission_required = None
    login_required = False
    object = None

    def has_permission(self, **kwargs):
        logic = self.permission_logic
        if "instance" not in kwargs:
            instance = self.get_object()
        else:
            instance = kwargs["instance"]
        if logic is None or instance is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_logic attribute. Define {0}.permission_required, or override '
                '{0}.get_permission_required().'.format(self.__class__.__name__)
            )
        else:
            self.permissions = logic(self.request, instance, **kwargs)
            return self.permissions.has_perm(self.permission_required)

    def handle_no_permission(self, authenticated=None):
        print("no permission for {}".format(self.permission_required))
        if authenticated is None:
            authenticated = self.request.user.is_authenticated
        if authenticated:
            return render(self.request, "error/404.html")
        else:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

    def dispatch(self, request, *args, **kwargs):
        if self.login_required and not request.user.is_authenticated:
            return self.handle_no_permission(authenticated=False)
        if not self.has_permission(**kwargs):
            return self.handle_no_permission()
        return super(ObjectPermissionsMixin, self).dispatch(request, *args, **kwargs)


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def get_json_response(self, response):
        data = {
            'pk': self.object.pk,
        }
        return data

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            content = render_to_string("generic/error_alert.html", {'form': form})
            return JsonResponse(content, safe=False, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = self.get_json_response(response)
            return JsonResponse(data)
        else:
            return response


class NewTemplateResponseMixin(TemplateResponseMixin):
    def get_template_names(self):
        self.template_name = self.kwargs.get("template_name") or self.template_name
        return super(NewTemplateResponseMixin, self).get_template_names()


class FormContextMixin(FormMixin):
    template_name = "single_content.html"
    form_title = None
    form_id = None
    form_action = None
    render_type = "form-table"
    submit_label = "Submit"
    success_url = None

    def get_form_kwargs(self):
        kwargs = super(FormContextMixin, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(FormContextMixin, self).get_context_data(**kwargs)
        form_id = self.form_id or self.form_title.lower().replace(" ", "_")
        form = {
            "title": self.form_title,
            "id": form_id,
            "action": self.form_action,
            "type": self.render_type,
            "form": ctx['form'],
            "props": "",
            "submit_label": self.submit_label,
            "submit_props": ""
        }
        ctx["template"] = "generic/form.html"
        ctx["args"] = form

        return ctx


class AjaxFormMixin(FormContextMixin):
    success_url = None
    template_name = "base.html"
    popup_template_name = "generic/popup_form.html"
    form_title = None
    object = None

    def get_referer(self, request):
        referer = request.META.get('HTTP_REFERER', None)
        if referer:
            return referer.split(self.request.META['HTTP_HOST'])[1]
        return "/"

    def get_popup(self, form):
        template_name = self.popup_template_name
        if not self.request.is_ajax():
            form["prev_url"] = self.referer
        return render_to_string(template_name, form, self.request)

    def get_context_data(self, **kwargs):
        ctx = super(AjaxFormMixin, self).get_context_data(**kwargs)
        ctx["args"]["form_action"] = self.request.path
        ctx["popup"] = self.get_popup(ctx["args"])
        ctx.pop("template")
        return ctx

    def popup_response(self, request, popup):
        view, args, kwargs = resolve(self.referer)
        kwargs['request'] = request
        kwargs['popup'] = popup
        return HttpResponse(view(*args, **kwargs).rendered_content)

    def get(self, request, *args, **kwargs):
        self.referer = self.get_referer(request)
        if request.is_ajax():
            return JsonResponse(self.get_context_data(**kwargs)['popup'], safe=False)
        else:
            return self.popup_response(request, self.get_context_data(**kwargs)['popup'])

    def get_json_response(self, response):
        data = {
            'pk': self.object.pk,
        }
        return data

    def form_invalid(self, form):
        response = super(AjaxFormMixin, self).form_invalid(form)
        if self.request.is_ajax():
            content = render_to_string("generic/error_alert.html", {'form': form})
            return JsonResponse(content, safe=False, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxFormMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = self.get_json_response(response)
            return JsonResponse(data)
        else:
            return response


class NewObjectView(AjaxFormMixin, CreateView):
    pass


class NewChildObjectView(ObjectPermissionsMixin, AjaxFormMixin, UpdateView):
    login_required = True

    def get_form_kwargs(self):
        kwargs = super(NewChildObjectView, self).get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.pop('instance', None)
            kwargs.update({'parent': self.object,
                           'request': self.request
                           })
        return kwargs

    def get_success_url(self):
        url = self.success_url
        if url is None:
            url = self.request.META.get('HTTP_REFERER', None) or "/"
        else:
            url = url.format({"pk": self.kwargs.get("pk")})
        return url

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(NewChildObjectView, self).get(request, *args, **kwargs)


class ProfileView(ObjectPermissionsMixin, DetailView):
    template_name = "profile/profile.html"
    permission_required = "view"
    login_required = True
    details = []
    stats = []
    tabs = []
    toolbar = []

    def get_details(self):
        instance = self.object
        details = []
        for name in self.details:
            value = None
            if name.endswith("__list"):
                name = name[:-6]
                object_list = getattr(instance, name, [])
                try:
                    object_list = object_list.all()
                except Exception:
                    continue
                value = render_to_string("profile/profile_dropdown.html", {"args": object_list})
            elif name.endswith("__versus"):
                name = name[:-8]
                object_list = getattr(instance, name, [])
                try:
                    object_list = object_list.all()
                except Exception:
                    continue
                value = render_to_string("competitions/profile_versus.html", {"args": object_list})
            elif name.endswith("__display"):
                name = name[:-9]
                value = getattr(instance, "get_{}_display".format(name), None)
                if value:
                    value = value().title()
            elif name.endswith("__link"):
                name = name[:-6]
                obj = getattr(instance, name, "")
                if obj:
                    value = '<a href="{}">{}</a>'.format(obj.get_absolute_url(), obj)
            elif name.endswith("__btn"):
                name = name[:-5]
                obj = getattr(instance, name, "")
                if obj:
                    value = render_to_string("profile/profile_button.html", {"args": obj, "display": "inline"})
            elif "__" in name:
                ending = name[name.find("__") + 1:]
                name = name[:name.find("__")]
                value = getattr(instance, name + ending, "")
            else:
                value = getattr(instance, name, "")
            if value:
                details.append((name.replace("_", " "), value))
        return details

    def get_stats(self):
        stats = []
        for name in self.stats:
            label = name.split("__")[-1].replace("_", " ")
            stat = get_attr_mult(self.object, name)
            stats.append((label, stat))
        return stats

    def get_toolbar(self):
        toolbar = []
        for index, btn_group in enumerate(deepcopy(self.toolbar)):
            btns = []
            for i, btn in enumerate(btn_group["btns"]):
                name = btn["name"]
                if self.permissions.has_perm(name):
                    args = btn.get("args", None)
                    kwargs = btn.get("kwargs", None)
                    if kwargs:
                        for key, value in kwargs.items():
                            if "__" in str(value):
                                kwargs[key] = get_attr_mult(self, value)
                            else:
                                kwargs[key] = self.kwargs.get(value, value)
                        btn["link"] = reverse(name, args=args, kwargs=kwargs)
                    else:
                        btn["link"] = reverse(name, args=args)
                    if "label" not in btn:
                        btn["label"] = name.replace("_", " ").replace("-", " ").title()
                    btns.append(deepcopy(btn))
            if len(btns) > 0:
                new_btn_group = deepcopy(btn_group)
                new_btn_group["btns"] = btns
                toolbar.append(new_btn_group)
        return toolbar

    def get_tabs(self):
        tabs = []
        pk = self.object.pk
        for i, tab in enumerate(self.tabs):
            tab = deepcopy(tab)
            tab_name = tab["name"]
            if self.permissions.has_perm(tab_name):
                view, args, kwargs = resolve(reverse(tab_name, kwargs={"pk": pk}))
                kwargs['request'] = self.request
                template_name = tab.get("template") or tab_name
                kwargs['template_name'] = "tabs/{}.html".format(template_name)
                try:
                    tab["content"] = view(*args, **kwargs).rendered_content
                    if "label" not in tab:
                        tab["label"] = tab_name.replace("_", " ").title()
                    if "badge" in tab:
                        badge = getattr(self.object, tab["badge"])
                        if type(badge) == int:
                            tab["badge"] = badge
                        elif type(badge) == list:
                            tab["badge"] = len(badge)
                        else:
                            tab["badge"] = badge.count()
                    tabs.append(deepcopy(tab))
                except Http404:
                    tab["content"] = ""
        return tabs

    def get_context_data(self, **kwargs):
        ctx = super(ProfileView, self).get_context_data(**kwargs)
        ctx["popup"] = self.kwargs.get("popup")
        ctx["toolbar"] = self.get_toolbar()
        ctx["header"] = {"details": self.get_details(),
                         "stats": self.get_stats()}
        ctx["navtabs"] = self.get_tabs()
        return ctx


class ListView(ObjectPermissionsMixin, DetailView):
    template_name = "base.html"
    include_template_name = None
    permission_required = "view"
    login_required = True
    object_list_attr = None
    list_model = None
    list_model_relationship = "m21"
    list_model_filters = {}

    def get_template_names(self):
        self.template_name = self.kwargs.get("template_name") or self.template_name
        return super(ListView, self).get_template_names()

    def get_object_list(self):
        if self.object_list_attr:
            if "__" in self.object_list_attr:
                object_list = get_attr_mult(self.object, self.object_list_attr)
            else:
                object_list = getattr(self.object, self.object_list_attr)
            if self.list_model:
                if self.list_model_relationship == "m21":
                    id_list = object_list.values_list(self.list_model.__name__.lower())
                    filters = deepcopy(self.list_model_filters)
                    filters["id__in"] = id_list
                    return self.list_model.objects.filter(**filters).all()
                elif self.list_model_relationship == "12m":
                    field = self.object_list_attr
                    id_list = object_list.values_list("id")
                    field = field[:-1] if field.endswith("s") else field
                    return self.list_model.objects.filter(**{"{}__in".format(field):
                                                             id_list})
            return object_list.all()
        return []

    def get_context_data(self, **kwargs):
        ctx = super(ListView, self).get_context_data(**kwargs)
        if self.include_template_name:
            ctx["template"] = self.include_template_name
        ctx["object_list"] = self.get_object_list()
        return ctx


class EditView(ObjectPermissionsMixin, AjaxFormMixin, UpdateView):
    submit_label = "Save"
    permission_required = "edit"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(EditView, self).get(request, *args, **kwargs)


class ActionView(ObjectPermissionsMixin, DetailView):
    success_url = None
    template_name = "base.html"
    popup_template_name = "generic/confirm_action.html"
    form_action = ""
    message_template = "emails/notification.html"
    notify_group = "owner"
    verb = ""
    past_verb = ""
    action_text = None

    def get_referer(self, request):
        referer = request.META.get('HTTP_REFERER', None)
        if referer:
            return referer.split(self.request.META['HTTP_HOST'])[1]
        return "/"

    def get_action_text(self, past=False):
        verb = self.verb
        if past:
            if self.past_verb:
                verb = self.past_verb
            else:
                verb += "d" if verb[-1] == "e" else "ed"

        if self.action_text:
            return self.action_text.format(verb)
        action_text = ""
        class_name = self.__class__.__name__
        for c in class_name:
            if c.isupper():
                action_text += " "
                c = c.lower()
            action_text += c
        return action_text.replace(self.verb, verb)

    def get_warning(self):
        return "Are you sure you want to {} {}?".format(
            self.get_action_text(),
            self.object)

    def get_errors(self):
        return False

    def send_notification(self):
        action_text = self.get_action_text(past=True)
        notify_group = self.notify_group
        subject = "{}: {}".format(action_text.title(), self.object)
        if notify_group == "owner":
            profiles = [getattr(self.object, self.permissions.owner)]
        else:
            profiles = getattr(self.object, self.notify_group)
        params = {
            "subject": subject,
            "template": self.message_template,
            "instance": self.object,
            "actor": self.request.user.profile,
            "action_text": action_text
        }
        for profile in profiles:
            params["user"] = profile.user
            send_notification(**params)

    def run_process(self, request, *args, **kwargs):
        pass

    def get_popup(self):
        template_name = self.popup_template_name
        ctx = {"errors": self.get_errors(),
               "warning": self.get_warning(),
               "form_action": self.form_action}
        if not self.request.is_ajax():
            ctx["prev_url"] = self.referer
        return render_to_string(template_name, ctx, self.request)

    def get_context_data(self, **kwargs):
        ctx = super(ActionView, self).get_context_data(**kwargs)
        ctx["popup"] = self.get_popup()
        return ctx

    def get_success_url(self):
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")

    def popup_response(self, request, popup):
        referer = request.META.get('HTTP_REFERER', None) or "/"
        view, args, kwargs = resolve(referer.split(request.META['HTTP_HOST'])[1])
        kwargs['request'] = request
        kwargs['popup'] = popup
        return HttpResponse(view(*args, **kwargs).rendered_content)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.referer = self.get_referer(request)
        if request.is_ajax():
            if self.referer:
                self.form_action = self.referer
            return JsonResponse(self.get_popup(), safe=False)
        else:
            return super(ActionView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        errors = self.get_errors()
        if not errors:
            self.run_process(request, *args, **kwargs)
            self.send_notification()
            success_url = self.get_success_url()
            return HttpResponseRedirect(success_url)
        return self.popup_response(request, None)


class BaseFormSetMixin(object):
    """
    Base class for constructing a FormSet within a view
    """

    initial = []
    form_class = None
    formset_class = None
    success_url = None
    extra = 0
    max_num = None
    can_order = False
    can_delete = False
    prefix = None

    def construct_formset(self):
        """
        Returns an instance of the formset
        """
        formset_class = self.get_formset()
        extra_form_kwargs = self.get_extra_form_kwargs()

        # Hack to let as pass additional kwargs to each forms constructor. Be aware that this
        # doesn't let us provide *different* arguments for each form
        if extra_form_kwargs:
            formset_class.form = wraps(formset_class.form)(partial(formset_class.form, **extra_form_kwargs))

        return formset_class(**self.get_formset_kwargs())

    def get_initial(self):
        """
        Returns the initial data to use for formsets on this view.
        """
        return self.initial

    def get_formset_class(self):
        """
        Returns the formset class to use in the formset factory
        """
        return self.formset_class

    def get_extra_form_kwargs(self):
        """
        Returns extra keyword arguments to pass to each form in the formset
        """
        return {}

    def get_form_class(self):
        """
        Returns the form class to use with the formset in this view
        """
        return self.form_class

    def get_formset(self):
        """
        Returns the formset class from the formset factory
        """
        return formset_factory(self.get_form_class(), **self.get_factory_kwargs())

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instantiating the formset.
        """
        kwargs = {}

        # We have to check whether initial has been set rather than blindly passing it along,
        # This is because Django 1.3 doesn't let inline formsets accept initial, and no versions
        # of Django let generic inline formset handle initial data.
        initial = self.get_initial()
        if initial:
            kwargs['initial'] = initial

        if self.prefix:
            kwargs['prefix'] = self.prefix

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = {
            'extra': self.extra,
            'max_num': self.max_num,
            'can_order': self.can_order,
            'can_delete': self.can_delete
        }

        if self.get_formset_class():
            kwargs['formset'] = self.get_formset_class()

        return kwargs


class FormSetMixin(BaseFormSetMixin, ContextMixin):
    """
    A mixin that provides a way to show and handle a formset in a request.
    """

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        if self.success_url:
            url = self.success_url
        else:
            # Default to returning to the same page
            url = self.request.get_full_path()
        return url

    def formset_valid(self, formset):
        """
        If the formset is valid redirect to the supplied URL
        """
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        """
        If the formset is invalid, re-render the context data with the
        data-filled formset and errors.
        """
        return self.render_to_response(self.get_context_data(formset=formset))


class ModelFormSetMixin(FormSetMixin, MultipleObjectMixin):
    """
    A mixin that provides a way to show and handle a model formset in a request.
    """

    exclude = None
    fields = None
    formfield_callback = None
    widgets = None

    def get_context_data(self, **kwargs):
        """
        If an object list has been supplied, inject it into the context with the
        supplied context_object_name name.
        """
        context = {}

        if self.object_list is not None:
            context['object_list'] = self.object_list
            context_object_name = self.get_context_object_name(self.object_list)
            if context_object_name:
                context[context_object_name] = self.object_list
        context.update(kwargs)

        # MultipleObjectMixin get_context_data() doesn't work when object_list
        # is not provided in kwargs, so we skip MultipleObjectMixin and call
        # ContextMixin directly.
        return ContextMixin.get_context_data(self, **context)

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instantiating the formset.
        """
        kwargs = super(ModelFormSetMixin, self).get_formset_kwargs()
        kwargs['queryset'] = self.get_queryset()
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = super(ModelFormSetMixin, self).get_factory_kwargs()
        kwargs.update({
            'exclude': self.exclude,
            'fields': self.fields,
            'formfield_callback': self.formfield_callback,
            'widgets': self.widgets,
        })
        if self.get_form_class():
            kwargs['form'] = self.get_form_class()
        if self.get_formset_class():
            kwargs['formset'] = self.get_formset_class()
        return kwargs

    def get_formset(self):
        """
        Returns the formset class from the model formset factory
        """
        return modelformset_factory(self.model, **self.get_factory_kwargs())

    def formset_valid(self, formset):
        """
        If the formset is valid, save the associated models.
        """
        self.object_list = formset.save()
        return super(ModelFormSetMixin, self).formset_valid(formset)


class BaseInlineFormSetMixin(BaseFormSetMixin):
    """
    Base class for constructing an inline formSet within a view
    """
    model = None
    inline_model = None
    fk_name = None
    formset_class = BaseInlineFormSet
    exclude = None
    fields = None
    formfield_callback = None
    can_delete = True
    save_as_new = False

    def get_context_data(self, **kwargs):
        """
        If an object has been supplied, inject it into the context with the
        supplied context_object_name name.
        """
        context = {}

        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context.update(kwargs)
        return super(BaseInlineFormSetMixin, self).get_context_data(**context)

    def get_inline_model(self):
        """
        Returns the inline model to use with the inline formset
        """
        return self.inline_model

    def get_formset_kwargs(self):
        """
        Returns the keyword arguments for instantiating the formset.
        """
        kwargs = super(BaseInlineFormSetMixin, self).get_formset_kwargs()
        kwargs['save_as_new'] = self.save_as_new
        kwargs['instance'] = self.object
        return kwargs

    def get_factory_kwargs(self):
        """
        Returns the keyword arguments for calling the formset factory
        """
        kwargs = super(BaseInlineFormSetMixin, self).get_factory_kwargs()
        kwargs.update({
            'exclude': self.exclude,
            'fields': self.fields,
            'formfield_callback': self.formfield_callback,
            'fk_name': self.fk_name,
        })
        if self.get_form_class():
            kwargs['form'] = self.get_form_class()
        if self.get_formset_class():
            kwargs['formset'] = self.get_formset_class()
        return kwargs

    def get_formset(self):
        """
        Returns the formset class from the inline formset factory
        """
        return inlineformset_factory(self.model, self.get_inline_model(), **self.get_factory_kwargs())


class InlineFormSetMixin(BaseInlineFormSetMixin, FormSetMixin, SingleObjectMixin):
    """
    A mixin that provides a way to show and handle a inline formset in a request.
    """

    def formset_valid(self, formset):
        self.object_list = formset.save()
        return super(InlineFormSetMixin, self).formset_valid(formset)


class ProcessFormSetView(View):
    """
    A mixin that processes a formset on POST.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the formset.
        """
        formset = self.construct_formset()
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a formset instance with the passed
        POST variables and then checked for validity.
        """
        formset = self.construct_formset()
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseFormSetView(FormSetMixin, ProcessFormSetView):
    """
    A base view for displaying a formset
    """


class FormSetView(TemplateResponseMixin, BaseFormSetView):
    """
    A view for displaying a formset, and rendering a template response
    """


class BaseModelFormSetView(ModelFormSetMixin, ProcessFormSetView):
    """
    A base view for displaying a model formset
    """
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(BaseModelFormSetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(BaseModelFormSetView, self).post(request, *args, **kwargs)


class ModelFormSetView(MultipleObjectTemplateResponseMixin, BaseModelFormSetView):
    """
    A view for displaying a model formset, and rendering a template response
    """


class BaseInlineFormSetView(InlineFormSetMixin, ProcessFormSetView):
    """
    A base view for displaying an inline formset for a queryset belonging to a parent model
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseInlineFormSetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseInlineFormSetView, self).post(request, *args, **kwargs)


class InlineFormSetView(SingleObjectTemplateResponseMixin, BaseInlineFormSetView):
    """
    A view for displaying an inline formset for a queryset belonging to a parent model
    """


class ManageView(InlineFormSetView):
    include_template_name = None
    add_form_class = None
    login_required = True
    template_name = "base.html"
    form_title = None
    form_id = None
    form_action = None
    render_type = "form-table"
    submit_label = "Submit"

    def get_success_url(self):
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)
        else:
            return self.request.get_full_path()

    def get_template_names(self):
        self.template_name = self.kwargs.get("template_name") or self.template_name
        return super(ManageView, self).get_template_names()

    def get_context_data(self, **kwargs):
        ctx = super(ManageView, self).get_context_data(**kwargs)
        form_id = self.form_id or self.form_title.lower().replace(" ", "_")
        form = {
            "title": self.form_title,
            "id": form_id,
            "action": self.form_action,
            "formset": ctx['formset'],
            "props": "",
            "submit_label": self.submit_label,
            "submit_props": "",
            "add_form": self.add_form_class(parent=self.object) if self.add_form_class else None
        }
        ctx["template"] = self.include_template_name
        ctx["args"] = form

        return ctx


def home(request):

    ctx = {"user": request.user,
           "styles": [{"link": "https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css"}],
           "scripts": [{"name": "js/bracketv2.js"}, {"name": "js/build_bracket.js"}],
           "template": "generic/grid.html",
           "contents": [
               {"template": "bracket_builder.html",
                "args": "",
                "row": "new",
                "col": [12, 8, 8, 7]
                },
               {"template": "socialapps/twitter_profile.html",
                "args": "",
                "col": [12, 4, 4, 5]
                },
           ],
           }

    return render(request, "base.html", ctx)


def home_files(request, filename):
    return render(request, "etc/" + filename, {}, content_type="text/plain")


def bracket_builder(request):
    content = {"title": "Bracket Builder"}
    return render(request, "bracket_builder_page.html", content)


def contact(request):
    title = 'Contact Us'
    form = ContactForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form_email = form.cleaned_data.get("email")
            inquiry_type = form.cleaned_data.get("inquiry_type")
            form_message = form.cleaned_data.get("message")
            form_full_name = form.cleaned_data.get("full_name")
            # print email, message, full_name
            subject = "Contact: " + inquiry_type
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, 'jgriffin@matchup-games.com']
            contact_message = "{}: {} via {}".format(
                form_full_name,
                form_message,
                form_email)

            send_mail(subject,
                      contact_message,
                      from_email,
                      to_email,
                      fail_silently=True)

            return HttpResponseRedirect("/")

    form = {
        "title": "Send Us A Message",
        "id": "contact",
        "classes": "",
        "type": "form-table",
        "content": form,
        "submit_label": "Send"
    }
    context = {
        "user": request.user,
        "title": title,
        "template": "generic/form.html",
        "args": form
    }

    return render(request, "single_content.html", context)

