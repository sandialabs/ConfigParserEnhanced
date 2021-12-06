<!-- Gitlab Badges -->
<!--
[![pipeline status](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/ConfigParserEnhanced/badges/master/pipeline.svg)](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/ConfigParserEnhanced/-/commits/master)
[![coverage report](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/ConfigParserEnhanced/badges/master/coverage.svg)](http://10.202.35.89:8080/ConfigParserEnhanced/coverage/index.html)
[![Generic badge](https://img.shields.io/badge/docs-latest-green.svg)](http://10.202.35.89:8080/ConfigParserEnhanced/doc/index.html)
-->

<!-- Github Badges -->
[![ConfigParserEnhanced Testing](https://github.com/sandialabs/ConfigParserEnhanced/actions/workflows/testing.yml/badge.svg)](https://github.com/sandialabs/ConfigParserEnhanced/actions/workflows/testing.yml)


ConfigParserEnhanced
====================

`ConfigParserEnhanced` (CPE) provides extended functionality for the `ConfigParser` module. This class attempts to satisfy the following goals:

1. Provide a framework to embed extended ‘parsing’ into `Config.ini` style files with customizable
   _handlers_ that allow 'commands' to be embedded into the key-value structure of typical `.ini`
   file options.
2. Enable chaining of `[SECTIONS]` within a single `.ini` file, which uses the parsing capability noted in (1).
3. Provide an extensible capability. We intend CPE to be used as a base class for other
   tools so that subclasses can add additional handlers for new ‘operations’ which can be used by the parser.

Configuration `.ini` File Enhancements
======================================
CPE allows `.ini` files to be augmented to embed commands into the `key: value`
structure of options within a section.

_Normal_ `.ini` files might have a structure that looks like this:

```ini
[SECTION NAME]
key1: value1
key2: value2
key4: value3
```

CPE augments this by allowing the **keys** to be used to embed _operations_.
To enable this, CPE attempts to split a key into three pieces, an _operation_, a _parameter_, and
an optional _uniqueifier_ string.  An option can have an operation extracted as
`<operation> <parameter> [uniquestr]: value` for example:

```ini
[SECTION NAME]
operation1 parameter1: value1
operation2 parameter2 A: value2
operation2 parameter2 B: value2
key1: value1
key2: value2
key3: value3
```

> **Note:** The `[uniquestr]` is optional and we can use it to prevent certain duplicate key errors from the
> underlying `ConfigParser` which requires that each section must have no duplicate 'key' fields.

When the CPE parser successfully identifies a potential _operation_, it will attempt to find a _handler_
method named as `_handler_<operation>()` or `handler_<operation>()`, and if one exists then it will execute
that handler with the detected parameter (if any) and value (if any) from that entry.

New handlers can be added by creating a subclass of CPE and then adding the new handlers to the subclass.

Operations
==========
The CPE base class provides the following handlers by default.

`use`
----
The `use` handler is used in the following manner:

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
See the [CHANGELOG](CHANGELOG.md) for information on changes.

Links
=====
Additional documentation can be found [here][1].

[1]: http://10.202.35.89:8080/ConfigParserEnhanced/doc/index.html
