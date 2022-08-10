
# Contents

- [Installation Notes](#installation-notes)
- [Using Operations and Block Paths Properly](#using-operations-and-block-paths-properly)
  - [Block Path](#block-path)
  - [Rename and Remove Operations](#rename-and-remove-operations)
  - [Alter Block Structure Operations](#alter-block-structure-operations)
  - [Other Operations](#other-operations)
- [Making Custom Operations](#making-custom-operations)
  - [Basic Usage](#basic-usage)
  - [block_value](#blockvalue)
  - [Making Structural Changes](#making-structural-changes)
  - [Old List Format](#old-list-format)

# Installation Notes

Note that the migration operation `MigrateStreamData` is dependent on the migrations of wagtailcore.
If a data migration containing `MigrateStreamData` is applied before the wagtailcore migrations have
been applied, you may get an error. 

# Using Operations and Block Paths Properly

The `MigrateStreamData` class takes a list of operations and corresponding block paths as a 
parameter `operations_and_block_paths`. Each operation in the list will be applied to all blocks
that match the corresponding block path.

```
operations_and_block_paths=[ 
    (operation1, block_path1),
    (operation2, block_path2),
    ... 
]
```

## Block Path

The block path is a `'.'` separated list of names of the block types from the top level StreamBlock (
the container of all the blocks in the StreamField) to the nested block type which will be matched 
and passed to the operation.

**NOTE:** If we want to directly operate on the top level StreamBlock, then the block path must be
an empty string `""`.

For example if our Stream definition looks like this,

```python
class MyDeepNestedBlock(StreamBlock):
    foo = CharBlock()
    date = DateBlock()

class MyNestedBlock(StreamBlock): 
    char1 = CharBlock()
    deepnested1 = MyDeepNestedBlock()

class MyStreamBlock(StreamBlock):
    field1 = CharBlock()
    nested1 = MyNestedBlock()

class MyPage(Page):
    content = StreamField(MyStreamBlock)
```

If we want to match all "field1" blocks, our block path will be `"field1"`,

```
[
    { "type": "field1", ... }, # this is matched
    { "type": "field1", ... }, # this is matched
    { "type": "nested1", "value": [...] },
    { "type": "nested1", "value": [...] },
    ...
]
```

If we want to match all "deepnested1" blocks, which are a direct child of "nested1", our block path
will be `"nested1.deepnested1"`,

```python
[
    { "type": "field1", ... },
    { "type": "field1", ... },
    { "type": "nested1", "value": [
        { "type": "char1", ... },
        { "type": "deepnested1", ... }, # This is matched
        { "type": "deepnested1", ... }, # This is matched
        ...
    ] },
    { "type": "nested1", "value": [
        { "type": "char1", ... },
        { "type": "deepnested1", ... }, # This is matched
        ...
    ] },
    ...
]
```

**NOTE**: When the path contains a ListBlock child, 'item' must be added to the block path as
the name of said child. For example, if we consider the following stream definition,

```
class MyStructBlock(StructBlock): 
    char1 = CharBlock()
    char2 = CharBlock()

class MyStreamBlock(StreamBlock):
    list1 = ListBlock(MyStructBlock())
```

Then if we want to match "char1", which is a child of the structblock which is the direct list 
child, we have to use `block_path_str="list1.item.char1"` instead of 
~~`block_path_str="list1.char1"`~~. We can also match the ListBlock child as such if we want with 
`block_path_str="list1.item"`.

## Rename and Remove Operations

The following operations are available from the package for renaming and removing blocks.

- `operations.RenameStreamChildrenOperation`
- `operations.RenameStructChildrenOperation`
- `operations.RemoveStreamChildrenOperation`
- `operations.RemoveStructChildrenOperation`

Note that all of these operations operate on the value of the parent block of the block which must
be removed or renamed. Hence make sure that the block path you are passing points to the parent 
block when using these operations.

## Alter Block Structure Operations

The following operations allow you to alter the structure of blocks in certain ways.

- `operations.StreamChildrenToListBlockOperation`  
    Operates on the value of a StreamBlock. Combines all child blocks of type `block_name` as 
    children of a single ListBLock which is a child of the parent StreamBlock.
- `operations.StreamChildrenToStreamBlockOperation`  
    Operates on the value of a StreamBlock. Note that `block_names` here is a list of block types 
    and not a single block type unlike `block_name` in the previous operation. Combines each child
    block of a type in `block_names` as children of a single StreamBlock which is a child of the 
    parent StreamBlock. 
- `operations.StreamChildrenToStructBlockOperation`  
    Moves each StreamBlock child of the given type inside a new StructBlock

    A new StructBlock will be created as a child of the parent StreamBlock for each child block of
    the given type, and then that child block will be moved from the parent StreamBlocks children
    inside the new StructBlock as a child of that StructBlock.
    
    For example, consider the following StreamField definition,

    ```
    mystream = StreamField([("char1", CharBlock()) ...], ...)
    ```

    Then the stream data would look like the following,

    ```
    [
        { "type": "char1", "value": "Value1", ... },
        { "type": "char1", "value": "Value2", ... },
        ...
    ]
    ```

    And if we define the operation like this,

    ```
    StreamChildrenToStructBlockOperation("char1", "struct1")
    ```

    Our altered stream data would look like this,

    ```
    [
        ...
        { "type": "struct1", "value": { "char1": "Value1" } },
        { "type": "struct1", "value": { "char1": "Value2" } },
        ...
    ]
    ```

    **NOTE:** Block ids are not preserved here since the new blocks are structurally different than 
    the previous blocks.


## Other Operations

- `operations.AlterBlockValueOperation`

# Making Custom Operations

## Basic Usage

While this package comes with a set of operations for common use cases, there may be many
instances where you need to define your own operation for mapping data. Making a custom operation
is fairly straightforward. All you need to do is extend the `BaseBlockOperation` class and 
define the `apply` method. 

For example, if we want to do something with the value of all matching blocks,

```python
from wagtail_streamfield_migration_toolkit.operations import BaseBlockOperation

class MyBlockOperation(BaseBlockOperation):
    def __init__(self, name):
        super().__init__()
        self.name = name
        
    def apply(self, block_value):
        # do something with the block value
        new_block_value = do_something(block_value)
        return new_block_value

```

## block_value

Note that depending on the type of block we're dealing with, the `block_value` which is passed to
`apply` may take different structures.

For non structural blocks, the value of the block will be passed directly.

The value passed to `apply` when the matched block is a StreamBlock would look like this,

```JSON
[
    { "type": "...", "value": "...", "id": "..." },
    { "type": "...", "value": "...", "id": "..." },
    ...
]
```

The value passed to `apply` when the matched block is a StructBlock would look like this,

```JSON
{
    "type1": "...",
    "type2": "...",
    ...
}
```

The value passed to `apply` when the matched block is a ListBlock would look like this,

```JSON
[
    { "type": "item", "value": "...", "id": "..." },
    { "type": "item", "value": "...", "id": "..." },
    ...
]
```

## Making Structural Changes

When making changes involving the structure of blocks (eg: changing block type), it may be needed
to operate on the block value of the parent block instead of the block to which the change is made,
since only the value of a block is changed by the `apply` operation.

Take a look at the implementation of the `RenameStreamChildrenOperation` for an example.

## Old list format

Prior to wagtail version 2.16 list block children were saved as just a normal python list of values. 
However for newer versions of wagtail, list block children are saved as ListValues. When handling
raw data, the changes would like the following,

old format

```python
[
    value1,
    value2,
    ...
]
```

new format

```python
[
    { "type": "item", "id": "...", "value": value1 },
    { "type": "item", "id": "...", "value": value2 },
    ...
]
```

When defining an operation that operates on a ListBlock value, in case you have old data which is
still in the old format, it is possible to use 
`wagtail_streamfield_migration_toolkit.utils.formatted_list_child_generator` to obtain the children
in the new format like so,

```python
    def apply(self, block_value):
        for child_block in formatted_list_child_generator(list_block_value):
            ...
```