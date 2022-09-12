# Wagtail streamfield-migration-toolkit

a set of reusable utilities to allow Wagtail implementors to easily generate data migrations for changes to StreamField block structure

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[![PyPI version](https://badge.fury.io/py/streamfield-migration-toolkit.svg)](https://badge.fury.io/py/streamfield-migration-toolkit)
[![Wagtail Hallo CI](https://github.com/wagtail/streamfield-migration-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/wagtail/streamfield-migration-toolkit/actions/workflows/test.yml)

# Contents

- [Introduction](#introduction)
  - [Why data migrations?](#why-data-migrations)
  - [Features](#features)
- [Quick Start](#quick-start)
- [Reference](docs/REFERENCE.md)
- [Usage](docs/USAGE.md)
- [Contributing](docs/CONTRIBUTING.md)

# Introduction

This package aims to make it easier for developers using StreamField who need to write data
migrations when making changes involving blocks/block structure in the StreamField. We expose a
custom migration operation class (`MigrateStreamData`) for migrations, which recurses through
a streamfield to apply chosen sub-operations to all blocks matching a specific type. With it we also 
supply a set of sub-operations to perform the most common changes, while also allowing you to
write your own when needed.

## Why Data Migrations?

A `StreamField` is stored as a single column of JSON data in the database. Blocks are stored as structures within the JSON, and can be nested. However, as far as django is concerned when making schema migrations, everything inside this column is just a string of JSON data and the schema doesn’t change regardless of the content/structure of the StreamField since it is the same field type before and after the change. Therefore whenever changes are made to StreamFields, any existing data must be changed into the required structure by using a data migration created manually by the user. If
the data is not migrated, even a simple change like renaming a block can result in old data being lost.

Generally, data migrations are done manually by making an empty migration file and writing the forward and backward functions for a RunPython command which will handle the logic for taking the previously saved JSON representation and converting it into the new JSON representation needed.

While this is fairly straightforward for a very simple and small change like changing the name of a CharBlock, where you could define two functions for mapping the data and loop through all the blocks in the StreamField checking whether they are the required block type and applying the mapper accordingly; this can easily get very complicated when nested blocks and multiple fields are involved.

This package would make it easier to write data migrations for streamfield changes by providing utilities
to recurse through various streamdata structures and map changes, in addition to having several "operations"
which also handle the logic for altering the data for common use cases like renaming, removing and altering
values of blocks.

## Features

- `MigrateStreamData` class which handles logic for recursing through streamfield structures, applying changes and saving for both instances and revisions.
- Set of sub operations for common use cases like renaming or removing blocks, altering block values, moving a block inside a new `StructBlock` etc.
- [Autodetect](docs/USAGE.md#streamchangedetect) changes (limited)

# Quick Start

## Installation

- `pip install wagtail-streamfield-migration-toolkit`
- Add `"wagtail_streamfield_migration_toolkit"` to `INSTALLED_APPS`

## Supported versions

- Python 3.7, 3.8, 3.9
- Django 3.2, 4.0
- Wagtail 3.0, 4.0

## Quick Usage

Assume we have a model `BlogPage` in app `blog`, defined as follows:

```python
class BlogPage(Page):
    content = StreamField([
        ("stream1", blocks.StreamBlock([
            ("field1", blocks.CharBlock())
        ])),
    ])
```

If we want to rename `field1` to `block1`, we would use the following migration,

```python
from django.db import migrations

from wagtail_streamfield_migration_toolkit.migrate_operation import MigrateStreamData
from wagtail_streamfield_migration_toolkit.operations import RenameStreamChildrenOperation

class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0069_log_entry_jsonfield'),
        ...
    ]

    operations = [
        MigrateStreamData(
            app_name="blog",
            model_name="BlogPage",
            field_name="content",
            operations_and_block_paths=[
                (RenameStreamChildrenOperation(old_name="field1", new_name="block1"), "stream1"),
            ]
        ),
    ]

```

Refer [Basic Usage](docs/USAGE.md/#basic-usage) for a longer explanation.

<br></br>

##### [This package was originally developed as a GSoC project](https://github.com/sandilsranasinghe/wagtail-streamfield-migration-toolkit/discussions/17)