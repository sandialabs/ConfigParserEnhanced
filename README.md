ConfigParserEnhanced
====================

The ConfigParserEnhanced provides extended functionality for the configparser module. This class attempts to satisfy the following goals:

1. Provide a framework to embed extended ‘parsing’ into Config.ini style files with customizable
   _handlers_ that allows 'commands' to be embedded into the key-value structure of a typical .ini
   file options.
2. Enable chaining of `[SECTIONS]` within a single .ini file which using the parsing capability noted in (1).
3. Provide an extensible capability. We intend ConfigParserEnhanced to be used as a base class for other 
  tools so that subclasses can add additional handlers for new ‘operations’ which can be used by the parser.

Configuration .ini File Enhancements
====================================
ConfigParserEnhanced allows `.ini` files to be augmented to embed commands into the key:value 
structure of options within a section.  

_Normal_ .ini files might have a structure that looks like this:

```ini
[SECTION NAME]
key1: value1
key2: value2
key4: value3
```

ConfigParserEnhanced (CPE) augments this by allowing the **keys** to be used to embed _operations_. 
To enable this, CPE attempts to split a key into three pieces, an _operation_, a _parameter_ and add
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

Note: The `[uniquestr]` is optional and we can use it to prevent certain duplicate-key errors from the 
underlying `configparser` parser which requires that each section must have no duplicate 'key' 
fields.

When the CPE parser successfully identifies a potential _operation_, it will attempt to find a _handler_ 
method named as `_handler_<operation>()` or `handler_<operation>()` and if one exists then we will execute
that handler with the detected parameter (if any) and value (if any) from that entry.

New handlers can be added by creating a subclass of ConfigParserEnhanced and adding new handlers.

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
use SECTION-A:
key-B1: value-B1
```

In this example, the entry `use SECTION-A:` that is inside `[SECTION-B]` instructs the core 
parser to recurse into `[SECTION-A]` and process it before moving on with the rest of the 
entries in `[SECTION-B]`.  In this example, accessing
`ConfigParserEnhanced.configparserenhanceddata['SECTION-B']` would return the following 
result:

```python
{
    'key-A1': 'value-A1',
    'key-A2': 'value-A2',
    'key-A3': 'value-A3',
    'key-B1': 'value-B1',
}
```


Links
=====
Additional documentation can be found [here][1]

[1]: http://10.202.35.89:8080/ConfigParserEnhanced/doc/index.html
