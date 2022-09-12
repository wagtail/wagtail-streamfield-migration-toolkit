# Table of Contents

* [wagtail\_streamfield\_migration\_toolkit.migrate\_operation](#wagtail_streamfield_migration_toolkit.migrate_operation)
  * [MigrateStreamData](#wagtail_streamfield_migration_toolkit.migrate_operation.MigrateStreamData)
    * [\_\_init\_\_](#wagtail_streamfield_migration_toolkit.migrate_operation.MigrateStreamData.__init__)
* [wagtail\_streamfield\_migration\_toolkit.operations](#wagtail_streamfield_migration_toolkit.operations)
  * [RenameStreamChildrenOperation](#wagtail_streamfield_migration_toolkit.operations.RenameStreamChildrenOperation)
  * [RenameStructChildrenOperation](#wagtail_streamfield_migration_toolkit.operations.RenameStructChildrenOperation)
  * [RemoveStreamChildrenOperation](#wagtail_streamfield_migration_toolkit.operations.RemoveStreamChildrenOperation)
  * [RemoveStructChildrenOperation](#wagtail_streamfield_migration_toolkit.operations.RemoveStructChildrenOperation)
  * [StreamChildrenToListBlockOperation](#wagtail_streamfield_migration_toolkit.operations.StreamChildrenToListBlockOperation)
  * [StreamChildrenToStreamBlockOperation](#wagtail_streamfield_migration_toolkit.operations.StreamChildrenToStreamBlockOperation)
  * [AlterBlockValueOperation](#wagtail_streamfield_migration_toolkit.operations.AlterBlockValueOperation)
  * [StreamChildrenToStructBlockOperation](#wagtail_streamfield_migration_toolkit.operations.StreamChildrenToStructBlockOperation)
* [wagtail\_streamfield\_migration\_toolkit.utils](#wagtail_streamfield_migration_toolkit.utils)
  * [InvalidBlockDefError](#wagtail_streamfield_migration_toolkit.utils.InvalidBlockDefError)
  * [map\_block\_value](#wagtail_streamfield_migration_toolkit.utils.map_block_value)
  * [map\_stream\_block\_value](#wagtail_streamfield_migration_toolkit.utils.map_stream_block_value)
  * [map\_struct\_block\_value](#wagtail_streamfield_migration_toolkit.utils.map_struct_block_value)
  * [map\_list\_block\_value](#wagtail_streamfield_migration_toolkit.utils.map_list_block_value)
  * [apply\_changes\_to\_raw\_data](#wagtail_streamfield_migration_toolkit.utils.apply_changes_to_raw_data)

<a id="wagtail_streamfield_migration_toolkit.migrate_operation"></a>

# wagtail\_streamfield\_migration\_toolkit.migrate\_operation

<a id="wagtail_streamfield_migration_toolkit.migrate_operation.MigrateStreamData"></a>

## MigrateStreamData Objects

```python
class MigrateStreamData(RunPython)
```

Subclass of RunPython for streamfield data migration operations

<a id="wagtail_streamfield_migration_toolkit.migrate_operation.MigrateStreamData.__init__"></a>

#### \_\_init\_\_

```python
def __init__(app_name,
             model_name,
             field_name,
             operations_and_block_paths,
             revisions_from=None,
             chunk_size=1024,
             **kwargs)
```

MigrateStreamData constructor

**Arguments**:

- `app_name` _str_ - Name of the app.
- `model_name` _str_ - Name of the model.
- `field_name` _str_ - Name of the streamfield.
  operations_and_block_paths (:obj:`list` of :obj:`tuple` of (:obj:`operation`, :obj:`str`)):
  List of operations and corresponding block paths to apply.
- `revisions_from` _:obj:`datetime`, optional_ - Only revisions created from this date
  onwards will be updated. Passing `None` updates all revisions. Defaults to `None`.
  Note that live and latest revisions will be updated regardless of what value this
  takes.
- `chunk_size` _:obj:`int`, optional_ - chunk size for queryset.iterator and bulk_update.
  Defaults to 1024.
- `**kwargs` - atomic, elidable, hints for superclass RunPython can be given
  

**Example**:

  Renaming a block named `field1` to `block1`::
  MigrateStreamData(
  app_name="blog",
  model_name="BlogPage",
  field_name="content",
  operations_and_block_paths=[
  (RenameStreamChildrenOperation(old_name="field1", new_name="block1"), ""),
  ],
  revisions_from=datetime.date(2022, 7, 25)
  ),

<a id="wagtail_streamfield_migration_toolkit.operations"></a>

# wagtail\_streamfield\_migration\_toolkit.operations

<a id="wagtail_streamfield_migration_toolkit.operations.RenameStreamChildrenOperation"></a>

## RenameStreamChildrenOperation Objects

```python
class RenameStreamChildrenOperation(BaseBlockOperation)
```

Renames all StreamBlock children of the given type

**Notes**:

  The `block_path_str` when using this operation should point to the parent StreamBlock
  which contains the blocks to be renamed, not the block being renamed.
  

**Attributes**:

- `old_name` _str_ - name of the child block type to be renamed
- `new_name` _str_ - new name to rename to

<a id="wagtail_streamfield_migration_toolkit.operations.RenameStructChildrenOperation"></a>

## RenameStructChildrenOperation Objects

```python
class RenameStructChildrenOperation(BaseBlockOperation)
```

Renames all StructBlock children of the given type

**Notes**:

  The `block_path_str` when using this operation should point to the parent StructBlock
  which contains the blocks to be renamed, not the block being renamed.
  

**Attributes**:

- `old_name` _str_ - name of the child block type to be renamed
- `new_name` _str_ - new name to rename to

<a id="wagtail_streamfield_migration_toolkit.operations.RemoveStreamChildrenOperation"></a>

## RemoveStreamChildrenOperation Objects

```python
class RemoveStreamChildrenOperation(BaseBlockOperation)
```

Removes all StreamBlock children of the given type

**Notes**:

  The `block_path_str` when using this operation should point to the parent StreamBlock
  which contains the blocks to be removed, not the block being removed.
  

**Attributes**:

- `name` _str_ - name of the child block type to be removed

<a id="wagtail_streamfield_migration_toolkit.operations.RemoveStructChildrenOperation"></a>

## RemoveStructChildrenOperation Objects

```python
class RemoveStructChildrenOperation(BaseBlockOperation)
```

Removes all StructBlock children of the given type

**Notes**:

  The `block_path_str` when using this operation should point to the parent StructBlock
  which contains the blocks to be removed, not the block being removed.
  

**Attributes**:

- `name` _str_ - name of the child block type to be removed

<a id="wagtail_streamfield_migration_toolkit.operations.StreamChildrenToListBlockOperation"></a>

## StreamChildrenToListBlockOperation Objects

```python
class StreamChildrenToListBlockOperation(BaseBlockOperation)
```

Combines StreamBlock children of the given type into a new ListBlock

**Notes**:

  The `block_path_str` when using this operation should point to the parent StreamBlock
  which contains the blocks to be combined, not the child block itself.
  

**Attributes**:

- `block_name` _str_ - name of the child block type to be combined
- `list_block_name` _str_ - name of the new ListBlock type

<a id="wagtail_streamfield_migration_toolkit.operations.StreamChildrenToStreamBlockOperation"></a>

## StreamChildrenToStreamBlockOperation Objects

```python
class StreamChildrenToStreamBlockOperation(BaseBlockOperation)
```

Combines StreamBlock children of the given types into a new StreamBlock

**Notes**:

  The `block_path_str` when using this operation should point to the parent StreamBlock
  which contains the blocks to be combined, not the child block itself.
  

**Attributes**:

- `block_names` _:obj:`list` of :obj:`str`_ - names of the child block types to be combined
- `stream_block_name` _str_ - name of the new StreamBlock type

<a id="wagtail_streamfield_migration_toolkit.operations.AlterBlockValueOperation"></a>

## AlterBlockValueOperation Objects

```python
class AlterBlockValueOperation(BaseBlockOperation)
```

Alters the value of each block to the given value

**Attributes**:

  new_value : new value to change to

<a id="wagtail_streamfield_migration_toolkit.operations.StreamChildrenToStructBlockOperation"></a>

## StreamChildrenToStructBlockOperation Objects

```python
class StreamChildrenToStructBlockOperation(BaseBlockOperation)
```

Move each StreamBlock child of the given type inside a new StructBlock

A new StructBlock will be created as a child of the parent StreamBlock for each child block of
the given type, and then that child block will be moved from the parent StreamBlocks children
inside the new StructBlock as a child of that StructBlock.

**Example**:

  Consider the following StreamField definition::
  
  mystream = StreamField([("char1", CharBlock()) ...], ...)
  
  Then the stream data would look like the following::
  
  [
  ...
  { "type": "char1", "value": "Value1", ... },
  { "type": "char1", "value": "Value2", ... },
  ...
  ]
  
  And if we define the operation like this::
  
  StreamChildrenToStructBlockOperation("char1", "struct1")
  
  Our altered stream data would look like this::
  
  [
  ...
  { "type": "struct1", "value": { "char1": "Value1" } },
  { "type": "struct1", "value": { "char1": "Value2" } },
  ...
  ]
  

**Notes**:

  The `block_path_str` when using this operation should point to the parent StreamBlock
  which contains the blocks to be combined, not the child block itself.
  

**Notes**:

  Block ids are not preserved here since the new blocks are structurally different than the
  previous blocks.
  

**Attributes**:

- `block_names` _str_ - names of the child block types to be combined
- `struct_block_name` _str_ - name of the new StructBlock type

<a id="wagtail_streamfield_migration_toolkit.utils"></a>

# wagtail\_streamfield\_migration\_toolkit.utils

<a id="wagtail_streamfield_migration_toolkit.utils.InvalidBlockDefError"></a>

## InvalidBlockDefError Objects

```python
class InvalidBlockDefError(Exception)
```

Exception for invalid block definitions

<a id="wagtail_streamfield_migration_toolkit.utils.map_block_value"></a>

#### map\_block\_value

```python
def map_block_value(block_value, block_def, block_path, operation, **kwargs)
```

Maps the value of a block.

**Arguments**:

  block_value:
  The value of the block. This would be a list or dict of children for structural blocks.
  block_def:
  The definition of the block.
  block_path:
  A '.' separated list of names of the blocks from the current block (not included) to
  the nested block of which the value will be passed to the operation.
  operation:
  An Operation class instance (extends `BaseBlockOperation`), which has an `apply` method
  for mapping values.
  

**Returns**:

  mapped_value:

<a id="wagtail_streamfield_migration_toolkit.utils.map_stream_block_value"></a>

#### map\_stream\_block\_value

```python
def map_stream_block_value(stream_block_value, block_def, block_path,
                           **kwargs)
```

Maps each child block in a StreamBlock value.

**Arguments**:

  stream_block_value:
  The value of the StreamBlock, a list of child blocks
  block_def:
  The definition of the StreamBlock
  block_path:
  A '.' separated list of names of the blocks from the current block (not included) to
  the nested block of which the value will be passed to the operation.
  
  Returns
  mapped_value:
  The value of the StreamBlock after mapping all the children.

<a id="wagtail_streamfield_migration_toolkit.utils.map_struct_block_value"></a>

#### map\_struct\_block\_value

```python
def map_struct_block_value(struct_block_value, block_def, block_path,
                           **kwargs)
```

Maps each child block in a StructBlock value.

**Arguments**:

  stream_block_value:
  The value of the StructBlock, a dict of child blocks
  block_def:
  The definition of the StructBlock
  block_path:
  A '.' separated list of names of the blocks from the current block (not included) to
  the nested block of which the value will be passed to the operation.
  
  Returns
  mapped_value:
  The value of the StructBlock after mapping all the children.

<a id="wagtail_streamfield_migration_toolkit.utils.map_list_block_value"></a>

#### map\_list\_block\_value

```python
def map_list_block_value(list_block_value, block_def, block_path, **kwargs)
```

Maps each child block in a ListBlock value.

**Arguments**:

  stream_block_value:
  The value of the ListBlock, a list of child blocks
  block_def:
  The definition of the ListBlock
  block_path:
  A '.' separated list of names of the blocks from the current block (not included) to
  the nested block of which the value will be passed to the operation.
  
  Returns
  mapped_value:
  The value of the ListBlock after mapping all the children.

<a id="wagtail_streamfield_migration_toolkit.utils.apply_changes_to_raw_data"></a>

#### apply\_changes\_to\_raw\_data

```python
def apply_changes_to_raw_data(raw_data, block_path_str, operation, streamfield,
                              **kwargs)
```

Applies changes to raw stream data

**Arguments**:

  raw_data:
  The current stream data (a list of top level blocks)
  block_path_str:
  A '.' separated list of names of the blocks from the top level block to the nested
  block of which the value will be passed to the operation.
  
  eg:- 'simplestream.struct1' would point to,
  [..., { type: simplestream, value: [..., { type: struct1, value: {...} }] }]
  
- `NOTE` - If we're directly applying changes on the top level stream block, then this will
  be "".
  
- `NOTE` - When the path contains a ListBlock child, 'item' must be added to the block as
  the name of said child.
  
  eg:- 'list1.item.stream1' where the list child is a StructBlock would point to,
  [
  ...,
  {
- `type` - list1,
- `value` - [
  {
- `type` - item,
- `value` - { ..., stream1: [...] }
  },
  ...
  ]
  }
  ]
  operation:
  A subclass of `operations.BaseBlockOperation`. It will have the `apply` method
  for applying changes to the matching block values.
  streamfield:
  The streamfield for which data is being migrated. This is used to get the definitions
  of the blocks.
  

**Returns**:

  altered_raw_data:

