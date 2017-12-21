from collections import deque
import re

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
            name_attr
        )

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
    def get(self, index):
        return None if index >= len(self) else self[index]

    def __setitem__(self, index, value):
        self += [None] * (index - len(self) + 1)
        super(MagicList, self).__setitem__(index, value)


def parse_post(post_dict):
    out = {}
    for name, value in post_dict.items():
        tmp = out
        if name.startswith('BROTZ'):
            keys = re.findall(r'\[(.+?)\]', name)
            for key, next_key in zip(keys, keys[1:] + [None]):
                if next_key is None:
                    tmp[key] = value
                    continue
                if key.isdigit():
                    key = int(key)
                if not tmp.get(key):
                    if next_key.isdigit():
                        tmp[key] = MagicList()
                    else:
                        tmp[key] = {}
                tmp = tmp[key]
    return out
