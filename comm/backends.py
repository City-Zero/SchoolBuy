import sys

from django.template.backends import jinja2 as jinja2backend
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.module_loading import import_string
import jinja2
import six


# Original link:
# https://code.djangoproject.com/attachment/ticket/24694/24694.py
__author__ = 'carljm'


class Jinja2Backend(jinja2backend.Jinja2):
    def __init__(self, params):
        self.context_processors = [
            import_string(p)
            for p in params['OPTIONS'].pop('context_processors', [])
        ]
        super(Jinja2Backend, self).__init__(params)

    def from_string(self, template_code):
        return Template(
            self.env.from_string(template_code), self.context_processors)

    def get_template(self, template_name):
        try:
            return Template(
                self.env.get_template(template_name), self.context_processors)
        except jinja2.TemplateNotFound as exc:
            six.reraise(TemplateDoesNotExist, TemplateDoesNotExist(exc.args),
                        sys.exc_info()[2])
        except jinja2.TemplateSyntaxError as exc:
            six.reraise(TemplateSyntaxError, TemplateSyntaxError(exc.args),
                        sys.exc_info()[2])


class Template(jinja2backend.Template):

    def __init__(self, template, context_processors):
        self.template = template
        self.context_processors = context_processors

    def render(self, context=None, request=None):
        if context is None:
            context = {}
        if request is not None:
            context['request'] = request
            lazy_csrf_input = csrf_input_lazy(request)
            context['csrf'] = lambda: lazy_csrf_input
            context['csrf_input'] = lazy_csrf_input
            context['csrf_token'] = csrf_token_lazy(request)
            for cp in self.context_processors:
                context.update(cp(request))
            #print(context)
        return self.template.render(context)

