# Wagtail streamfield-migration-toolkit

a set of reusable utilities to allow Wagtail implementors to easily generate data migrations for changes to StreamField block structure


[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[![PyPI version](https://badge.fury.io/py/streamfield-migration-toolkit.svg)](https://badge.fury.io/py/streamfield-migration-toolkit)
[![Wagtail Hallo CI](https://github.com/wagtail/streamfield-migration-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/wagtail/streamfield-migration-toolkit/actions/workflows/test.yml)

# Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Reference](docs/REFERENCE.md)
- [Usage](docs/USAGE.md)
- [Contributing](docs/CONTRIBUTING.md)

# Introduction

This package aims to make it easier for developers using StreamField who need to write data 
migrations when making changes involving blocks/block structure in the StreamField. We expose a 
set of utilities for commonly made changes such as renaming or removing blocks, as well as utility
functions for recursing through existing Streamfield data and applying changes, which makes it 
easier to create custom logic for applying changes too.

# Quick Start

## Installation

- `pip install streamfield-migration-toolkit`
- Add `"wagtail_streamfield_migration_toolkit"` to `INSTALLED_APPS`

## Supported versions

- Python 3.7, 3.8, 3.9
- Django 3.2, 4.0
- Wagtail 4.0

## Quick Usage

Assume we have a model `BlogPage` in app `blog` which has a streamfield `content` with a child 
streamblock named `mystream` which has a child char block named `field1` which we want to rename to 
`block1`.

```python
from django.db import migrations

from wagtail_streamfield_migration_toolkit.migrate_operation import MigrateStreamData
from wagtail_streamfield_migration_toolkit.operations import RenameStreamChildrenOperation

class Migration(migrations.Migration):

    dependencies = [
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

<!-- TODO link to discussion for GSoC -->