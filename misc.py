import re
from HTMLParser import HTMLParser

from brotz import BaseTag, Div, Ul, Li, Empty, tag_str_to_class
from jinja2 import Environment, Template, nodes

jinja_env = Environment()

foo = 'bar'
l = [1, 2, 3]


jinja_str = '''
<div id="foo-id">
    {{ foo }}
</div>
<ul>
    {% for x in l %}
    <li>{{ x }}</li>
    {% endfor %}
</ul>
'''

b = Empty(
    Div(id="foo-id")(foo),
    Ul(Li(x) for x in l))


template = Template(jinja_str)
rendered_jinja = template.render(foo=foo, l=l)
rendered_brotz = str(b)


class Data(object):
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return '<Data: "{!r}">'.format(self.data)

    def _as_code(self):
        return repr(self.data)


class Code(object):
    def __init__(self, code):
        self.code = code

    def __repr__(self):
        return '<Code: {}>'.format(self.code)

    def _as_code(self):
        return self.code


class HtmlToLinearBrotz(HTMLParser):
    def parse(self, html):
        self.l = []
        self.feed(html)
        return self.l

    def handle_starttag(self, tag, attrs):
        brotz_tag = tag_str_to_class[tag](**dict(attrs))
        brotz_tag.is_start = True
        self.l.append(brotz_tag)

    def handle_endtag(self, tag):
        brotz_tag = tag_str_to_class[tag]()
        brotz_tag.is_start = False
        self.l.append(brotz_tag)

    def handle_data(self, data):
        if not data.isspace():
            self.l.append(Data(data))


def jinja_template_to_brotz_str(jinja_str):
    html_parser = HtmlToLinearBrotz()
    tree = jinja_env.parse(jinja_str)

    def yielder(tree):
        for node in tree.body:
            # handle general output
            if isinstance(node, nodes.Output):
                output = node
                for node in output.nodes:
                    if isinstance(node, nodes.TemplateData):
                        for n in html_parser.parse(node.data):
                            yield n
                    elif isinstance(node, nodes.Name):
                        yield Code(node.name)
            # handle for loops
            elif isinstance(node, nodes.For):
                for n in yielder(node):
                    yield n
                # node.body
                yield Code('for {x} in {y}'.format(
                    x=node.target.name,
                    y=node.iter.name,
                ))
            else:
                raise Warning("don't know how to process {}".format(node))

    l = list(yielder(tree))

    def inner(l):
        if not l:
            return []
        first = l[0]
        if not isinstance(first, BaseTag):
            return l
        children = l[1:]
        relevant_children = []
        for _ in range(len(children)):
            child = children.pop(0)
            if isinstance(child, first.__class__) and child.is_start is False:
                return [first(inner(relevant_children))] + inner(children)
            relevant_children.append(child)

    code = Empty(inner(l))._as_code()
    print 'Empty(Div(id="foo-id")(foo), Ul(Li(x) for x in l))'
    print code


jinja_template_to_brotz_str(jinja_str)


def test_eq():
    no_whitespace = re.sub(r'[ \n]', '', rendered_jinja)
    assert no_whitespace == rendered_brotz.replace(' ','')
