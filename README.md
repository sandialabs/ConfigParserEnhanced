<!-- Github Badges -->
[![ConfigParserEnhanced Testing](https://github.com/sandialabs/ConfigParserEnhanced/actions/workflows/test-driver-core.yml/badge.svg)](https://github.com/sandialabs/ConfigParserEnhanced/actions/workflows/test-driver-core.yml)
[![Documentation Status](https://readthedocs.org/projects/configparserenhanced/badge/?version=latest)](https://configparserenhanced.readthedocs.io/en/latest/?badge=latest)



ConfigParserEnhanced
====================

The ConfigParserEnhanced (CPE) package provides extended
handling of .ini files beyond what [ConfigParser][1] provides
by adding an active syntax to embed operations with options.

For example, a *standard* `.ini` file is generally formatted like this:

```ini
[Section 1]
Foo: Bar
Baz: Bif

[Section 2]
Foo: Bar2
Bif: Baz
```

These files are used to organize sets of key - value pairs called
“options” within groups called “sections”. In the example above
there are two sections, “Section 1” and “Section 2”. Each of them
contains two options where Section 1 has the keys ‘Foo’ and ‘Baz’
which are assigned the values ‘Bar’ and ‘Bif’, respectively. For
more details on .ini files please see the documentation for
ConfigParser.

Internally, these handlers methods defined according to a naming
convention like `handler_<operation>()`.

CPE only provides one pre-defined operation: use which is formatted as
`use TARGET:` where *param1* is the TARGET (there is no value field for this
one). The TARGET paramter takes the *name of a target section* that will be
loaded in at this point. This works in the same way a `#include` would
work in C++ and serves to insert the contents or processing of the
target section into this location.

The `use` operation is useful for .ini files for complex systems by allowing
developers to create a common section and then have specializations where
they can customize options for a given project. For example:

```ini
[COMMON]
Key C1: Value C1
Key C2: Value C2
Key C3: Value C3

[Data 1]
Key D1: Value D1
use COMMON
Key D2: Value D2
```

In this example, processing section `Data 1` via CPE will result in
the following options: `Key D1: Value D1`, `Key C1: Value C1`,
`Key C2: Value C2`, `Key C2: Value C2`, `Key D2: Value D2`.

An alternative way of looking at this is it’s like having a .ini file that
is effectively the following where the `use` operations are replaced with the
results of a Depth-First expansion of the linked sections:

```ini
[COMMON]
Key C1: Value C1
Key C2: Value C2
Key C3: Value C3

[Data 1]
Key D1: Value D1
Key C1: Value C1
Key C2: Value C2
Key C3: Value C3
Key D2: Value D2
```

Examples
--------
Here we show some example usages of ConfigParserEnhanced.
Additional examples can be found in the [`examples/`](examples) directory
of the repository.

### Example 1

```ini
[SECTION-A]
key-A1: value-A1
key-A2: value-A2
key-A3: value-A3

[SECTION-B]
use SECTION-A
key-B1: value-B1
```

In this example, the entry `use SECTION-A` that is inside `[SECTION-B]` instructs the core
parser to recurse into `[SECTION-A]` and process it before moving on with the rest of the
entries in `[SECTION-B]`.  In this example the following code could be used to parse
`SECTION-B`.
`ConfigParserEnhanced.configparserenhanceddata['SECTION-B']` would return the following
result:

```python
>>> from configparserenhanced import ConfigParserEnhanced
>>> cpe = ConfigParserEnhanced(filename='config.ini')
>>> cpe.configparserenhanceddata['SECTION-B']
{
    'key-A1': 'value-A1',
    'key-A2': 'value-A2',
    'key-A3': 'value-A3',
    'key-B1': 'value-B1',
}
```

Updates
=======
See the [CHANGELOG][2] for information on changes.


[1]: https://docs.python.org/3/library/configparser.html
[2]: https://github.com/sandialabs/ConfigParserEnhanced/blob/master/CHANGELOG.md
