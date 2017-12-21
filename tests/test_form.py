from brotz import Form, Ul, Li, Input, exists, not_exists
import brotz.form

fake_data_in = {
    'customer': {
        'name': 'Oli',
        'street': 'London Road',
        'group': {'type': 'best-customers'},
        'product': [
            {
                'name': 'dog',
                'price': 21.0,
                'to-delete': False,
                'dimension': [
                    {'width': 3},
                    {'width': 2},
                    {'width': 0},
                ]
            },
            {
                'name': 'cat',
                'price': 42.0,
                'to-delete': True,
                'dimension': [
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
    Ul(brotz.form.NestedList('product',
        Li(
            Input(name='name', value='dog'),
            Input(name='price', value=21.0),
            Input(name='to-delete', type='checkbox', checked=not_exists),
            brotz.form.NestedList('dimension',
                Input(name='width', value=3),
                Input(name='width', value=2),
                Input(name='width', value=0))
        ),
        Li(
            Input(name='name', value='cat'),
            Input(name='price', value=42.0),
            Input(name='to-delete', type='checkbox', checked=exists),
            brotz.form.NestedList('dimension',
                Input(name='width', value=5))
        ),
    ))
))


def test_parents_added():
    oli_input = nested_form.children[0].children[0]
    assert oli_input.attributes['value'] == 'Oli'

    group_nested = nested_form.children[0].children[2]
    assert group_nested.obj_name == 'group'
    assert group_nested.form_parent_strs == ['customer']

    dimension_nested_list = nested_form.children[0].children[3].children[0].children[0].children[3]
    assert dimension_nested_list.obj_name == 'dimension'
    assert dimension_nested_list.form_parent_strs == ['customer', 'product', '0']


def test_form_render():
    form_str = str(nested_form)
    assert form_str.split('><') == [
        '<form',
            'input name="BROTZ[customer][name]" value="Oli"', '/input',
            'input name="BROTZ[customer][street]" value="London Road"', '/input',
            'input name="BROTZ[customer][group][type]" value="best-customers"', '/input',
            'ul',
                'li',
                    'input name="BROTZ[customer][product][0][name]" value="dog"', '/input',
                    'input name="BROTZ[customer][product][0][price]" value="21.0"', '/input',
                    'input  type="checkbox" name="BROTZ[customer][product][0][to-delete]"', '/input',
                    'input name="BROTZ[customer][product][0][dimension][0][width]" value="3"', '/input',
                    'input name="BROTZ[customer][product][0][dimension][1][width]" value="2"', '/input',
                    'input name="BROTZ[customer][product][0][dimension][2][width]" value="0"', '/input',
                '/li',
                'li',
                    'input name="BROTZ[customer][product][1][name]" value="cat"', '/input',
                    'input name="BROTZ[customer][product][1][price]" value="42.0"', '/input',
                    'input checked type="checkbox" name="BROTZ[customer][product][1][to-delete]"', '/input',
                    'input name="BROTZ[customer][product][1][dimension][0][width]" value="5"', '/input',
                '/li',
            '/ul',
        '/form>',
    ]


fake_post_from_form = {
    'BROTZ[customer][name]': 'Oli',
    'BROTZ[customer][street]': 'London Road',
    'BROTZ[customer][group][type]': 'best-customers',
    'BROTZ[customer][product][0][name]': 'dog',
    'BROTZ[customer][product][0][price]': '21.0',
    'BROTZ[customer][product][0][dimension][0][width]': '3',
    'BROTZ[customer][product][0][dimension][1][width]': '2',
    'BROTZ[customer][product][0][dimension][2][width]': '0',
    'BROTZ[customer][product][1][name]': 'cat',
    'BROTZ[customer][product][1][price]': '42.0',
    'BROTZ[customer][product][1][to-delete]': 'on',
    'BROTZ[customer][product][1][dimension][0][width]': '5',
}

expected_data_out = {
    'customer': {
        'name': 'Oli',
        'street': 'London Road',
        'group': {'type': 'best-customers'},
        'product': [
            {
                'name': 'dog',
                'price': '21.0',
                'dimension': [
                    {'width': '3'},
                    {'width': '2'},
                    {'width': '0'},
                ]
            },
            {
                'name': 'cat',
                'price': '42.0',
                'to-delete': 'on',
                'dimension': [
                    {'width': '5'}
                ]
            }
        ]
    }
}


def test_parse_post():
    assert brotz.form.parse_post(fake_post_from_form) == expected_data_out


def test_marshmallowed():
    from marshmallow import Schema, fields

    class Dimension(Schema):
        width = fields.Int()

    class Product(Schema):
        name = fields.Str()
        price = fields.Float()
        to_delete = fields.Bool(
            attribute='to-delete', dump_to='to-delete', default=False)
        dimension = fields.Nested(Dimension(), many=True)

    class Group(Schema):
        type = fields.Str()

    class Customer(Schema):
        name = fields.Str()
        street = fields.Str()
        group = fields.Nested(Group())
        product = fields.Nested(Product(), many=True)

    assert Customer().dump(
        expected_data_out['customer']).data == fake_data_in['customer']

