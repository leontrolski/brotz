import cgi
from types import GeneratorType


exists = object()
not_exists = object()


class Raw(str):
    pass


class BaseTag(object):
    tag_name = ''
    is_start = None

    @staticmethod
    def _to_string(thing):
        if isinstance(thing, Raw) or not isinstance(thing, str):
            return str(thing)
        return cgi.escape(thing)

    @property
    def opening_str(self):
        return '<{tag_name}{attributes}>'.format(
            tag_name=self.tag_name,
            attributes=self._attributes_str,
        )

    @property
    def closing_str(self):
        return '</{tag_name}>'.format(tag_name=self.tag_name)

    @property
    def _attributes_str(self):
        if not self.attributes:
            return ''
        return ' ' + ' '.join(
            '' if value is not_exists else
            '{}{}'.format(
                name.replace('class_', 'class').replace('_', '-'),
                '' if value is exists else '="{}"'.format(self._to_string(value)))
            for name, value in self.attributes.iteritems()
        )

    @property
    def inner_str(self):
        return ''.join(self._to_string(child) for child in self.children)

    def __init__(self, *args, **attributes):
        self.children = []
        self._add_children(args)
        self.attributes = attributes

    def __call__(self, *args, **attributes):
        self._add_children(args)
        self.attributes.update(attributes)
        return self

    def _add_children(self, args):
        if isinstance(args, (list, tuple, GeneratorType)):
            for child in args:
                self._add_children(child)
        else:
            if isinstance(args, BaseTag):
                args.parent = self
            self.children.append(args)

    def __str__(self):
        return self.opening_str + self.inner_str + self.closing_str

    def __repr__(self):
        return '<{}{}>'.format(
            '/' if self.is_start is False else '',
            self.tag_name.capitalize())

    def __eq__(self, other):
        return str(self) == str(other)

    # WIP quining stuff, not stable
    @property
    def _attributes_code(self):
        if not self.attributes:
            return ''
        return '({})'.format(', '.join(
            '{}{}'.format(
                name.replace('class_', 'class'),
                '' if value == no_value else '="{}"'.format(self._to_string(value)))
            for name, value in self.attributes.iteritems()
        ))

    @property
    def _class_name(self):
        return self.tag_name.capitalize()

    def _as_code(self):
        return '{}{}({})'.format(
            self._class_name,
            self._attributes_code,
            ', '.join(child._as_code() for child in self.children),
        )


def make_tag_class(name, base_class=BaseTag):
    return type(name.capitalize(), (base_class, ), {'tag_name': name})


def make_tag_classes(names, base_class=BaseTag):
    return [make_tag_class(name, base_class) for name in names]


class T(object):
    """Wrap value so that None values and missing attrs return `default`."""
    def __init__(self, value, default=''):
        self.value = value
        self.default = default

    def __getattr__(self, item):
        try:
            return getattr(self.value, item)
        except AttributeError:
            return self.default

    def __str__(self):
        if self.value is None:
            return str(self.default)
        return str(self.value)
