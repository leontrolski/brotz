from collections import deque

from . import BaseTag, Empty


def yield_until_nested(tag):
    if isinstance(tag, BaseTag) and not isinstance(tag, BaseNested):
        yield tag
        for child in tag.children:
            for n in yield_until_nested(child):
                yield n


def yield_only_nested(tag):
    if isinstance(tag, BaseNested):
        yield tag
    for child in tag.children:
        for n in yield_only_nested(child):
            yield n


def add_parents_to_children(tag):
    for i, child in enumerate(tag.children):
        for n in yield_only_nested(child):
            if isinstance(tag, NestedList):
                n.form_parents.appendleft(i)
            n.form_parents.appendleft(tag)


class BaseNested(Empty):
    is_list = False

    def __init__(self, obj_name, *args, **kwargs):
        self.obj_name = obj_name
        self.nest_index = None
        self.form_parents = deque()
        super(BaseNested, self).__init__(*args, **kwargs)
        add_parents_to_children(self)

    @property
    def form_parent_strs(self):
        return [
            p.obj_name if isinstance(p, BaseNested) else str(p)
            for p in self.form_parents]

    def nested_name(self, name_attr, i):
        return 'BROTZ{}[{}]{}[{}]'.format(
            ''.join('[{}]'.format(p) for p in self.form_parent_strs),
            self.obj_name,
            '[{}]'.format(i) if self.is_list else '',
            name_attr)

    @property
    def inner_str(self):
        for i, child in enumerate(self.children):
            for n in yield_until_nested(child):
                attrs = n.attributes
                if 'name' in attrs:
                    # mutate other tag's attributes, urgh
                    attrs['name'] = self.nested_name(attrs['name'], i)
        return super(BaseNested, self).inner_str


class Nested(BaseNested):
    def __repr__(self):
        return '<Nested: {}>'.format(self.obj_name)


class NestedList(BaseNested):
    is_list = True

    def __repr__(self):
        return '<NestedList: {}>'.format(self.obj_name)


class MagicList(list):
    def __setitem__(self, key, value):
        try:
            super(MagicList, self).__setitem__(key, value)
        except IndexError:
            self.append(None)
            self.__setitem__(key, value)


class DefaultDictList(object):
    def __init__(self):
        self.value = None

    def init(self, key):
        if isinstance(key, int):
            if self.value is None:
                self.value = MagicList()
            elif not isinstance(self.value, list):
                raise RuntimeError('cant construct DefaultList')
        else:
            if self.value is None:
                self.value = {}
            elif not isinstance(self.value, dict):
                raise RuntimeError('cant construct DefaultDict')

    def __getitem__(self, item):
        self.init(item)
        return self

    def __setitem__(self, key, value):
        self.init(key)
        self.value[key] = value

