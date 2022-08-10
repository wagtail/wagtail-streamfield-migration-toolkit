# Contents

- [Migrate Stream Data](#migrate-stream-data)
- [Operations](#operations)

# Migrate Stream Data

`from wagtail_streamfield_migration_toolkit.migrate_operation import MigrateStreamData`

Subclass of RunPython for streamfield data migration operations.

```
MigrateStreamData(
    app_name,
    model_name,
    field_name,
    operations_and_block_paths,
    revisions_from=None,
    chunk_size=1024,
    **kwargs
)
```

### app_name

**String**. Name of the app. 

### model_name

**String**. Name of the model.

### field_name

**String**. The name of the streamfield.

### operations_and_block_paths

**List of tuples of (operation, block_path)**. List of operations and corresponding block paths to 
apply.

### revisions_from

**Datetime | None**. Only revisions created from this date onwards will be updated. Passing `None` 
updates all revisions. Defaults to `None`.

### chunk_size

**Integer**. chunk size for `queryset.iterator` and `bulk_update`. Defaults to 1024.

*Example*

```python
# Renaming a block named `field1` to `block1`
MigrateStreamData(
    app_name="blog",
    model_name="BlogPage",
    field_name="content",
    operations_and_block_paths=[
        (RenameStreamChildrenOperation(old_name="field1", new_name="block1"), ""),
    ],
)
```

# Operations

`from wagtail_streamfield_migration_toolkit import operations`

An Operation class contains the logic for mapping old data to new data. All Operation classes 
should extend the `BaseBlockOperation` class.

An Operation class has an `apply` method which determines how changes are applied to the
block/s we want to change. This method is called for the value of all blocks matching the given 
block path. 

```
    def apply(self, block_value):
```

### block_value

The value of matching blocks is passed as an argument to the `apply` method, which is responsible 
for applying changes to the children of the matching blocks and returning the altered values. 
Note that **we are dealing with raw data here**, not block objects, so our values have a JSON like 
structure, similar to what `StreamValue().raw_data` gives. 

The following operations are available and can be imported from 
`wagtail_streamfield_migration_toolkit.operations`.

- RenameStreamChildrenOperation  
    #### old_name 
    **String**. Name of the child block type to be renamed

    #### new_name 
    **String**. New name to rename to

- RenameStructChildrenOperation
    #### old_name 
    **String**. Name of the child block type to be renamed

    #### new_name 
    **String**. New name to rename to

- RemoveStreamChildrenOperation
    #### name 
    **String**. Name of the child block type to be removed

- RemoveStructChildrenOperation
    #### name 
    **String**. Name of the child block type to be removed

- StreamChildrenToListBlockOperation
    #### block_name 
    **String**. Name of the child block type to be combined

    #### list_block_name 
    **String**. Name of the new ListBlock type

- StreamChildrenToStreamBlockOperation
    #### block_names 
    **List of String**. Names of the child block types to be combined
    
    #### stream_block_name 
    **String**. Name of the new StreamBlock type

- StreamChildrenToStructBlockOperation
    #### block_names 
    **String**. Names of the child block types to be combined

    #### struct_block_name 
    **String**. Name of the new StructBlock type

- AlterBlockValueOperation
    #### new_value 
    New value to change to

It is possible to make your own custom operations by extending the `BaseBlockOperation` class 
and defining the `apply` method as needed. Refer [here](USAGE.md#making-custom-operations) 
for examples.
