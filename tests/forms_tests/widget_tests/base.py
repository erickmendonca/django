import os

from django import forms
from django.forms.renderers.templates import TemplateRenderer
from django.template.backends.django import DjangoTemplates
from django.test import SimpleTestCase
from django.utils.functional import cached_property

try:
    import jinja2
except ImportError:
    jinja2 = None
else:
    from django.template.backends.jinja2 import Jinja2

ROOT = os.path.join(os.path.dirname(forms.__file__), 'templates')


class DjangoRenderer(TemplateRenderer):

    @cached_property
    def engine(self):
        return DjangoTemplates({
            'APP_DIRS': False,
            'DIRS': [
                os.path.join(os.path.dirname(forms.__file__), 'templates'),
            ],
            'NAME': 'djangoforms',
            'OPTIONS': {},
        })


class Jinja2Renderer(TemplateRenderer):

    @cached_property
    def engine(self):
        return Jinja2({
            'APP_DIRS': False,
            'DIRS': [
                os.path.join(os.path.dirname(forms.__file__), 'jinja2'),
            ],
            'NAME': 'djangoforms',
            'OPTIONS': {},
        })


class WidgetTest(SimpleTestCase):
    beatles = (('J', 'John'), ('P', 'Paul'), ('G', 'George'), ('R', 'Ringo'))

    @classmethod
    def setUpClass(cls):
        cls.django_renderer = DjangoRenderer()
        cls.jinja2_renderer = Jinja2Renderer() if jinja2 else None
        super(WidgetTest, cls).setUpClass()

    def check_html(self, widget, name, value, html='', attrs=None, fix_quotes=False,
                   test_once=False, **kwargs):
        if self.jinja2_renderer:
            output = widget.render(
                name, value, attrs=attrs, renderer=self.jinja2_renderer, **kwargs
            )
            # Normalize quote escaping between Jinja2 and DTL
            output = output.replace("&#34;", "&quot;")
            self.assertHTMLEqual(output, html)

        if jinja2 and test_once:
            return

        output = widget.render(
            name, value, attrs=attrs, renderer=self.django_renderer, **kwargs
        )
        self.assertHTMLEqual(output, html)
