from collections import defaultdict

from brotz import (
    Div, Form, Ul, Li, Table, Th, Tr, Td, Input, br, exists, not_exists)
import brotz.form
from werkzeug.datastructures import ImmutableMultiDict

list_ = Ul(Li(class_='fancy')(n) for n in range(3))


data = [
    ['beavis', 2, 3],
    ['&', 5, 6],
]

table = Table(class_='table-sm', data_parent='dog')(
    Tr(Th('a'), Th('b'), Th('c')),
    (Tr(Td(cell) for cell in row) for row in data)
)

page = Div(id='wrapper', class_='page')(
    list_,
    table,
    br,
    Input(value='butthead', checked=exists),
    Input(value='buttshoe', checked=not_exists),
)

page_str = str(page)
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

# test brotz.form

data_in = {
    'customer': {
        'name': 'Oli',
        'street': 'London Road',
        'group': {'type': 'best-customers'},
        'product': [
            {
                'name': 'dog',
                'price': '21.0',
                'to-delete': False,
                'dimension': [
                    {'width': '3'},
                    {'width': '2'},
                    {'width': '0'},
                ]
            },
            {
                'name': 'cat',
                'price': '42.0',
                'to-delete': True,
                'dimension': [
                    {'width': '5'}
                ]
            }
        ]
    }
}

nested_form = Form(brotz.form.Nested('customer',
    Input(name='name', value='Oli'),
    Input(name='street', value='London Road'),
    brotz.form.Nested('group',
        Input(name='type', value='best-customers')),
    Ul(brotz.form.NestedList('product',
        Li(
            Input(name='name', value='dog'),
            Input(name='price', value='21.0'),
            Input(name='to-delete', type='checkbox', checked=not_exists),
            brotz.form.NestedList('dimension',
                Input(name='width', value='3'),
                Input(name='width', value='2'),
                Input(name='width', value='0'))
        ),
        Li(
            Input(name='name', value='cat'),
            Input(name='price', value='42.0'),
            Input(name='to-delete', type='checkbox', checked=exists),
            brotz.form.NestedList('dimension',
                Input(name='width', value='5'))
        ),
    ))
))

form_str = str(nested_form)

assert form_str == (
    '<form>'
        '<input name="brotz_customer_name" value="Oli"></input>'
        '<input name="brotz_customer_street" value="London Road"></input>'
        '<input name="brotz_group_type" value="best-customers"></input>'
        '<ul>'
            '<li>'
                '<input name="brotz_product_name" value="dog"></input>'
                '<input name="brotz_product_price" value="21.0"></input>'
                '<input  type="checkbox" name="brotz_product_to-delete" value="0"></input>'
                '<input name="brotz_dimension_0_width" value="3"></input>'
                '<input name="brotz_dimension_0_width" value="2"></input>'
                '<input name="brotz_dimension_0_width" value="0"></input>'
            '</li>'
            '<li>'
                '<input name="brotz_product_name" value="cat"></input>'
                '<input name="brotz_product_price" value="42.0"></input>'
                '<input checked type="checkbox" name="brotz_product_to-delete" value="1"></input>'
                '<input name="brotz_dimension_1_width" value="5"></input>'
            '</li>'
        '</ul>'
    '</form>'
)

fake_post_from_form = ImmutableMultiDict((
    ('brotz_customer_name', ['Oli']),
    ('brotz_customer_street', ['London Road']),
    ('brotz_group_type', ['best-customers']),
    ('brotz_product_name', ['dog', 'cat']),
    ('brotz_product_price', ['21.0', '42.0']),
    ('brotz_checkbox_product_to-delete', ['1']),
    ('brotz_dimension_0_width', ['3', '2', '0']),
    ('brotz_dimension_1_width', ['5']),
))

structured_data = defaultdict(lambda: defaultdict(dict))

for k, v in fake_post_from_form.items():
    if k.startswith('brotz_'):
        is_checkbox = False
        split = k.split('_')
        split.pop(0)
        if split[0] == 'checkbox':
            split.pop(0)
            v = [int(n) for n in v]
            split[-1] += '_checkbox'
        obj_name = split.pop(0)
        original_name = split.pop()
        nest_indexes = tuple(int(n) for n in split)
        structured_data[obj_name][nest_indexes][original_name] = v

data_shape = {'customer': (
    'group',
    {('product', ): (('dimension',),)},
)}

data_out = {}
data_out['customer'] = {
    'name': structured_data['customer'][()]['name'][0],
    'street': structured_data['customer'][()]['street'][0],
    'group': {'type': structured_data['group'][()]['type'][0]}
}
data_out['customer']['product'] = [
    {
        'name': structured_data['product'][()]['name'][i],
        'price':  structured_data['product'][()]['price'][i],
        'to-delete':  i in structured_data['product'][()]['to-delete_checkbox'],
        'dimension':  [
            {'width': w} for w in structured_data['dimension'][(i,)]['width']],
    } for i in (0, 1)]


assert data_out == data_in


def structured_data_to_data_out(data_shape, structured_data, level=0):
    d = {}
    for k, v in data_shape.items():
        if isinstance(k, str):
            d[k] = {}
            for original_name in structured_data[k][()]:
                d[k][original_name] = structured_data[k][()][original_name][0]
            for tuple_el in v:
                if isinstance(tuple_el, str):
                    d[k][tuple_el] = {}
                    for other_original_name in structured_data[tuple_el][()]:
                        d[k][tuple_el][other_original_name] = structured_data[tuple_el][()][other_original_name][0]
                elif isinstance(tuple_el, tuple):
                    print 'inner tuple', tuple_el
                elif isinstance(tuple_el, dict):
                    print 'inner dict', tuple_el
                    print structured_data_to_data_out(tuple_el, structured_data)
        elif isinstance(k, tuple):
            d[k[0]] = []

            for original_name in structured_data[k[0]][()]:
                if original_name.endswith('checkbox'):
                    pass

                import pdb; pdb.set_trace()
                print 'tuple inner', original_name

            print 'outer tuple', k, d, structured_data[k[0]]
            # return k
    return d

print structured_data_to_data_out(data_shape, structured_data)



