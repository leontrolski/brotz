# brotz

### _The ideas of `brotz` have been implemented more thoroughly in https://github.com/fabiommendes/hyperpython - some more thought could still be given to the form impedence mismatch thingy though._

Html templates suck, `brotz` is a lightweight, chiller, composable way to generate html in python.
For example: `str(Ul(id='some-ul')(Li(n) for n in [1, 2, 3]))` will give `'<ul id="some-ul"><li>1</li><li>2</li><li>3</li></ul>'`.

A further example:

```python
from brotz import exists
from brotz.tags import Div, Ul, Li, Table, Th, Tr, Td, Input, br

list_ = Ul(Li(class_='fancy')(n) for n in range(3))

data = [
    ['beavis', 2, 3],
    ['&', 5, 6],
]

table = Table(class_='table-sm')(
    Tr(Th('a'), Th('b'), Th('c')),
    (Tr(Td(cell) for cell in row) for row in data)
)

page = Div(id='wrapper', class_='page')(
    list_,
    table,
    br,
    Input(value='butthead', checked=exists),
)
```

`str(page)` gives you:

```html
<div class="page" id="wrapper">
    <ul>
        <li class="fancy">0</li>
        <li class="fancy">1</li>
        <li class="fancy">2</li>
    </ul>
    <table class="table-sm">
        <tr><th>a</th><th>b</th><th>c</th></tr>
        <tr><td>beavis</td><td>2</td><td>3</td></tr>
        <tr><td>&amp;</td><td>5</td><td>6</td></tr>
    </table>
    <br>
    <input checked value="butthead"></input>
</div>
```

A tag can be instantiated (and then optionally called) with arguments and keyword arguments. 
- Non-keyword args set the content of the tag, any generators/lists/tuples are recursively flattened, any strings not wrapped in `brotz.Raw()` are cgi escaped.
- Keyword arguments set attribute=value pairs, 'class_' is replaced with 'class', underscores are replaced with dashes and values are cgi escaped.
- Setting a keyword argument to `brotz.exists` makes an attribute with no value, `brotz.not_exists` nothing at all.
- A helper class `brotz.T` is provided that catches `None` values and attribute errors, eg: `str(Div(T([]).foo))` will just return `'<div></div>'`

Tag elements have `.attributes` (`dict`), `.children` (`list`), `.parent` (`brotz.BaseTag`), `.opening_str`, `.inner_str`, `.closing_str` public properties.

`brotz` has no dependencies.

# brotz.form

brotz.form sorts out the html form<->object impedence mismatch:
- Wrap brotz structures with `brotz.form.Nested` and `brotz.form.NestedList`.
- On `str`-ifying, any `name` attributes in these wrapped structures are prefixed with `"BROTZ"` and have `[attribute/index]`s added to them.
- Serve the form.
- The form is GET/POSTed to the server as `dict` with name eg: `form_data`
- `brotz.form.parse_post(form_data)` returns the data in the correct stucture.

Try follow the examples in [`tests/test_form.py`](tests/test_form.py) to get the idea

# development

run `py.test` to run tests.

# thanks

brotz was heavily inspired by [mithril](https://github.com/MithrilJS/mithril.js), thanks Leo!
