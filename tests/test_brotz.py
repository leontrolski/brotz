from brotz import T, exists, not_exists
from brotz.tags import Div, Ul, Li, Table, Th, Tr, Td, Input, br


data = [
    ['beavis', 2, 3],
    ['&', 5, 6],
]


def make_page():
    list_ = Ul(Li(class_='fancy')(n) for n in range(3))

    table = Table(class_='table-sm', data_parent='dog')(
        Tr(Th('a'), Th('b'), Th('c')),
        (Tr(Td(cell) for cell in row) for row in data)
    )

    return Div(id='wrapper', class_='page')(
        list_,
        table,
        br,
        Input(value='butthead', checked=exists),
        Input(value='buttshoe', checked=not_exists),
    )


def test_page():
    page_str = str(make_page())
    assert page_str == (
        '<div class="page" id="wrapper">'
            '<ul>'
                '<li class="fancy">0</li>'
                '<li class="fancy">1</li>'
                '<li class="fancy">2</li>'
            '</ul>'
            '<table class="table-sm" data-parent="dog">'
                '<tr><th>a</th><th>b</th><th>c</th></tr>'
                '<tr><td>beavis</td><td>2</td><td>3</td></tr>'
                '<tr><td>&amp;</td><td>5</td><td>6</td></tr>'
            '</table>'
            '<br>'
            '<input checked value="butthead"></input>'
            '<input  value="buttshoe"></input>'
        '</div>'
    )


def test_attribute_error():
    assert str(Div(T([]).whut.where, 42)) == '<div>42</div>'
    assert str(Div(T(None, 'haha'), 84)) == '<div>haha84</div>'
