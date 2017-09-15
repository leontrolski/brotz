from . import BaseTag, Empty, Form as FormTag


def is_nested_tag(tag):
    return isinstance(tag, Nested) or isinstance(tag, NestedList)


def raise_underscore_error(name):
    if '_' in name:
        raise RuntimeError('underscore not allowed in name "{}"'.format(name))


def yield_until_nested(tag):
    if isinstance(tag, BaseTag) and not is_nested_tag(tag):
        yield tag
        for child in tag.children:
            for n in yield_until_nested(child):
                yield n


def yield_only_nested(tag):
    if is_nested_tag(tag):
        yield tag
    for child in tag.children:
        for n in yield_only_nested(child):
            yield n


def add_nest_indexes_to_children(tag):
    # not sure this will work properly for nesting, write tests
    for i, child in enumerate(tag.children):
        for n in yield_only_nested(child):
            n.nest_indexes.append(i)


def add_brotz_naming_to_children(tag):
    nest_indexing = ''
    if tag.nest_indexes:
        nest_indexing = '{}_'.format('_'.join(str(i) for i in tag.nest_indexes))

    for i, child in enumerate(tag.children):
        for n in yield_until_nested(child):
            attrs = n.attributes
            if 'name' in attrs:
                raise_underscore_error(attrs['name'])
                new_name = 'brotz_{}_{}{}'.format(
                    tag.obj_name, nest_indexing, attrs['name'])
                attrs['name'] = new_name
            if 'type' in attrs:
                if attrs['type'] == 'checkbox':
                    attrs['value'] = i


class Nested(Empty):
    def __init__(self, obj_name, *args, **kwargs):
        raise_underscore_error(obj_name)
        self.obj_name = obj_name
        self.nest_indexes = []
        super(Nested, self).__init__(*args, **kwargs)

    @property
    def inner_str(self):
        add_brotz_naming_to_children(self)
        return super(Nested, self).inner_str


class NestedList(Empty):
    def __init__(self, obj_name, *args, **kwargs):
        raise_underscore_error(obj_name)
        self.obj_name = obj_name
        self.nest_indexes = []
        super(NestedList, self).__init__(*args, **kwargs)

    @property
    def inner_str(self):
        add_nest_indexes_to_children(self)
        add_brotz_naming_to_children(self)
        return super(NestedList, self).inner_str
