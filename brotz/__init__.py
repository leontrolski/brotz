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


class Empty(BaseTag):
    opening_str = ''
    closing_str = ''
    _class_name = 'Empty'


def make_tag_class(name, base_class=BaseTag):
    return type(name.capitalize(), (base_class, ), {'tag_name': name})


def make_tag_classes(names, base_class=BaseTag):
    return [make_tag_class(name, base_class) for name in names]


br = Raw('<br>')

# from https://www.w3schools.com/TAGs/
tag_strs = (
    'a',
    'abbr',
    'acronym',
    'address',
    'applet',
    'area',
    'article',
    'aside',
    'audio',
    'b',
    'base',
    'basefont',
    'bdi',
    'bdo',
    'big',
    'blockquote',
    'body',
    'br',
    'button',
    'canvas',
    'caption',
    'center',
    'cite',
    'code',
    'col',
    'colgroup',
    'datalist',
    'dd',
    'del',
    'details',
    'dfn',
    'dialog',
    'dir',
    'div',
    'dl',
    'dt',
    'em',
    'embed',
    'fieldset',
    'figcaption',
    'figure',
    'font',
    'footer',
    'form',
    'frame',
    'frameset',
    'h1',
    'head',
    'header',
    'hr',
    'html',
    'i',
    'iframe',
    'img',
    'input',
    'ins',
    'kbd',
    'keygen',
    'label',
    'legend',
    'li',
    'link',
    'main',
    'map',
    'mark',
    'menu',
    'menuitem',
    'meta',
    'meter',
    'nav',
    'noframes',
    'noscript',
    'object',
    'ol',
    'optgroup',
    'option',
    'output',
    'p',
    'param',
    'picture',
    'pre',
    'progress',
    'q',
    'rp',
    'rt',
    'ruby',
    's',
    'samp',
    'script',
    'section',
    'select',
    'small',
    'source',
    'span',
    'strike',
    'strong',
    'style',
    'sub',
    'summary',
    'sup',
    'table',
    'tbody',
    'td',
    'textarea',
    'tfoot',
    'th',
    'thead',
    'time',
    'title',
    'tr',
    'track',
    'tt',
    'u',
    'ul',
    'var',
    'video',
)
tag_classes = make_tag_classes(tag_strs)
(
    A,
    Abbr,
    Acronym,
    Address,
    Applet,
    Area,
    Article,
    Aside,
    Audio,
    B,
    Base,
    Basefont,
    Bdi,
    Bdo,
    Big,
    Blockquote,
    Body,
    Br,
    Button,
    Canvas,
    Caption,
    Center,
    Cite,
    Code,
    Col,
    Colgroup,
    Datalist,
    Dd,
    Del,
    Details,
    Dfn,
    Dialog,
    Dir,
    Div,
    Dl,
    Dt,
    Em,
    Embed,
    Fieldset,
    Figcaption,
    Figure,
    Font,
    Footer,
    Form,
    Frame,
    Frameset,
    H1,
    Head,
    Header,
    Hr,
    Html,
    I,
    Iframe,
    Img,
    Input,
    Ins,
    Kbd,
    Keygen,
    Label,
    Legend,
    Li,
    Link,
    Main,
    Map,
    Mark,
    Menu,
    Menuitem,
    Meta,
    Meter,
    Nav,
    Noframes,
    Noscript,
    Object,
    Ol,
    Optgroup,
    Option,
    Output,
    P,
    Param,
    Picture,
    Pre,
    Progress,
    Q,
    Rp,
    Rt,
    Ruby,
    S,
    Samp,
    Script,
    Section,
    Select,
    Small,
    Source,
    Span,
    Strike,
    Strong,
    Style,
    Sub,
    Summary,
    Sup,
    Table,
    Tbody,
    Td,
    Textarea,
    Tfoot,
    Th,
    Thead,
    Time,
    Title,
    Tr,
    Track,
    Tt,
    U,
    Ul,
    Var,
    Video,
) = tag_classes

tag_str_to_class = {
    tag_str: class_ for tag_str, class_ in zip(tag_strs, tag_classes)}
