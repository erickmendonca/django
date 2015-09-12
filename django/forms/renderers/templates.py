import os

from django import forms
from django.apps import apps
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.template.loader import get_template
from django.template.loaders import app_directories
from django.utils.functional import cached_property

try:
    import jinja2
except ImportError:
    jinja2 = None

ROOT = os.path.join(os.path.dirname(forms.__file__), 'jinja2')


class TemplateRenderer(object):
    engine_name = None

    @cached_property
    def engine(self):
        if self.engine_name is not None:
            return engines[self.engine_name]

        if templates_configured():
            return

        if not jinja2:
            # TODO: Add RemovedInDjango20Warning indicating this will be removed.
            return DjangoTemplates({
                'APP_DIRS': False,
                'DIRS': [
                    os.path.join(os.path.dirname(forms.__file__), 'templates'),
                ],
                'NAME': 'djangoforms',
                'OPTIONS': {},
            })

        # TODO: RemovedInDjango20Warning indicating this will be removed and
        # TEMPLATES should be modified to include this Engine?
        return self.default_engine()

    @staticmethod
    def default_engine():
        from django.template.backends.jinja2 import Jinja2
        return Jinja2({
            'APP_DIRS': False,
            'DIRS': [ROOT],
            'NAME': 'djangoforms',
            'OPTIONS': {},
        })

    @property
    def loader(self):
        engine = self.engine
        if engine is None:
            return get_template
        else:
            return engine.get_template

    def render(self, template_name, context, request=None):
        template = self.loader(template_name)
        return template.render(context, request=request).strip()


def templates_configured():
    installed = False
    app_dirs = False

    for app_config in apps.get_app_configs():
        if app_config.name == 'django.forms':
            installed = True
            break

    for engine in engines.all():
        if engine.app_dirs is True:
            app_dirs = True

        if isinstance(engine, DjangoTemplates):
            for loader in engine.engine.template_loaders:
                if isinstance(loader, app_directories.Loader):
                    app_dirs = True

        if app_dirs:
            break

    return installed and app_dirs
