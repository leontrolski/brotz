from brotz import Form, Ul, Li, Input, exists, not_exists
import brotz.form
import pytest


def test_a_small_bit():
    form = brotz.form.NestedList(
        'animals', (Input(name='name', value=a) for a in ['dog', 'cat']))

    assert str(form) == (
        '<input name="BROTZ[animals][0][name]" value="dog"></input>'
        '<input name="BROTZ[animals][1][name]" value="cat"></input>'
    )
    assert brotz.form.parse_post({
        'BROTZ[animals][0][name]': 'dog',
        'BROTZ[animals][1][name]': 'cat',
    }) == {'animals': [{'name': 'dog'}, {'name': 'cat'}]}


def test_nested_lists():
    form = brotz.form.NestedList('a',
        brotz.form.NestedList('b', (Input(name='name') for _ in [None, None])),
        brotz.form.NestedList('c', (Input(name='name') for _ in [None, None, None])),
    )
    assert str(form) == (
        '<input name="BROTZ[a][0][b][0][name]"></input>'
        '<input name="BROTZ[a][0][b][1][name]"></input>'
        '<input name="BROTZ[a][1][c][0][name]"></input>'
        '<input name="BROTZ[a][1][c][1][name]"></input>'
        '<input name="BROTZ[a][1][c][2][name]"></input>'
    )


fake_data_in = {
    'customer': {
        'name': 'Oli',
        'street': 'London Road',
        'group': {'type': 'best-customers'},
        'products': [
            {
                'name': 'dog',
                'price': 21.0,
                'to-delete': False,
                'dimensions': [
                    {'width': 3},
                    {'width': 2},
                    {'width': 0},
                ]
            },
            {
                'name': 'cat',
                'price': 42.0,
                'to-delete': True,
                'dimensions': [
                    {'width': 5}
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
    Ul(brotz.form.NestedList('products',
        Li(
            Input(name='name', value='dog'),
            Input(name='price', value=21.0),
            Input(name='to-delete', type='checkbox', checked=not_exists),
            brotz.form.NestedList('dimensions',
                Input(name='width', value=3),
                Input(name='width', value=2),
                Input(name='width', value=0))
        ),
        Li(
            Input(name='name', value='cat'),
            Input(name='price', value=42.0),
            Input(name='to-delete', type='checkbox', checked=exists),
            brotz.form.NestedList('dimensions',
                Input(name='width', value=5))
        ),
    ))
))

expected_form_split = [
    '<form',
        'input name="BROTZ[customer][name]" value="Oli"', '/input',
        'input name="BROTZ[customer][street]" value="London Road"', '/input',
        'input name="BROTZ[customer][group][type]" value="best-customers"', '/input',
        'ul',
            'li',
                'input name="BROTZ[customer][products][0][name]" value="dog"', '/input',
                'input name="BROTZ[customer][products][0][price]" value="21.0"', '/input',
                'input  type="checkbox" name="BROTZ[customer][products][0][to-delete]"', '/input',
                'input name="BROTZ[customer][products][0][dimensions][0][width]" value="3"', '/input',
                'input name="BROTZ[customer][products][0][dimensions][1][width]" value="2"', '/input',
                'input name="BROTZ[customer][products][0][dimensions][2][width]" value="0"', '/input',
            '/li',
            'li',
                'input name="BROTZ[customer][products][1][name]" value="cat"', '/input',
                'input name="BROTZ[customer][products][1][price]" value="42.0"', '/input',
                'input checked type="checkbox" name="BROTZ[customer][products][1][to-delete]"', '/input',
                'input name="BROTZ[customer][products][1][dimensions][0][width]" value="5"', '/input',
            '/li',
        '/ul',
    '/form>',
]


def test_parents_added():
    oli_input = nested_form.children[0].children[0]
    assert oli_input.attributes['value'] == 'Oli'

    group_nested = nested_form.children[0].children[2]
    assert group_nested.obj_name == 'group'
    assert group_nested.form_parent_strs == ['customer']

    dimension_nested_list = nested_form.children[0].children[3].children[0].children[0].children[3]
    assert dimension_nested_list.obj_name == 'dimensions'
    assert dimension_nested_list.form_parent_strs == ['customer', 'products', '0']


def test_form_render():
    form_str = str(nested_form)
    assert form_str.split('><') == expected_form_split


def test_form_render_again():
    # make sure there's no persistent mutation
    form_str = str(nested_form)
    assert form_str.split('><') == expected_form_split


fake_post_from_form = {
    'BROTZ[customer][name]': 'Oli',
    'BROTZ[customer][street]': 'London Road',
    'BROTZ[customer][group][type]': 'best-customers',
    'BROTZ[customer][products][0][name]': 'dog',
    'BROTZ[customer][products][0][price]': '21.0',
    'BROTZ[customer][products][0][dimensions][0][width]': '3',
    'BROTZ[customer][products][0][dimensions][1][width]': '2',
    'BROTZ[customer][products][0][dimensions][2][width]': '0',
    'BROTZ[customer][products][1][name]': 'cat',
    'BROTZ[customer][products][1][price]': '42.0',
    'BROTZ[customer][products][1][to-delete]': 'on',
    'BROTZ[customer][products][1][dimensions][0][width]': '5',
}

expected_data_out = {
    'customer': {
        'name': 'Oli',
        'street': 'London Road',
        'group': {'type': 'best-customers'},
        'products': [
            {
                'name': 'dog',
                'price': '21.0',
                'dimensions': [
                    {'width': '3'},
                    {'width': '2'},
                    {'width': '0'},
                ]
            },
            {
                'name': 'cat',
                'price': '42.0',
                'to-delete': 'on',
                'dimensions': [
                    {'width': '5'}
                ]
            }
        ]
    }
}


def test_parse_post():
    assert brotz.form.parse_post(fake_post_from_form) == expected_data_out


def test_marshmallowed():
    try:
        from marshmallow import Schema, fields
    except ImportError:
        pytest.xfail('marshmallow not installed, cannot run test')

    class Dimension(Schema):
        width = fields.Int()

    class Product(Schema):
        name = fields.Str()
        price = fields.Float()
        to_delete = fields.Bool(
            attribute='to-delete', dump_to='to-delete', default=False)
        dimensions = fields.Nested(Dimension(), many=True)

    class Group(Schema):
        type = fields.Str()

    class Customer(Schema):
        name = fields.Str()
        street = fields.Str()
        group = fields.Nested(Group())
        products = fields.Nested(Product(), many=True)

    assert Customer().dump(
        expected_data_out['customer']).data == fake_data_in['customer']
