Html templates suck, `brotz` is a lightweight, chiller way to compose html in python, eg:

```
from brotz import Div, Ul, Li, Table, Th, Tr, Td, Input, br, no_value

list_ = Ul(Li(class_='fancy')(n) for n in range(3))
# str(list_) -> <ul><li class="fancy">0</li><li class="fancy">1</li><li class="fancy">2</li></ul>

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
    Input(value='butthead', checked=no_value),
)
```

`str(page)` gives you: `<div class="page" id="wrapper"><ul><li class="fancy">0</li><li class="fancy">1</li><li class="fancy">2</li></ul><table class="table-sm"><tr><th>a</th><th>b</th><th>c</th></tr><tr><td>beavis</td><td>2</td><td>3</td></tr><tr><td>&amp;</td><td>5</td><td>6</td></tr></table><br><input checked value="butthead"></input></div>`

A tag can be instantiated (and then optionally called) with arguments and keyword arguments. 
- Non-keyword args set the content of the tag, any generators/lists/tuples are recursively flattened, any strings not wrapped in `brotz.Raw()` are cgi escaped.
- Keyword arguments set attribute=value pairs, 'class_' is replaced with 'class', underscores are replaced with dashes and values are cgi escaped.

Tag elements have `.attributes` (`dict`), `.children` (`list`), `.parent` (`brotz.BaseTag`), `.opening_str`, `.inner_str`, `.closing_str` public properties.

`brotz` has no dependencies.