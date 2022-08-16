class StreamDefinitionComparer:
    def __init__(self, old_streamblock_def, new_streamblock_def):
        self.old_streamblock_def = old_streamblock_def
        self.new_streamblock_def = new_streamblock_def
        # to keep track of mappings for which we need to make an operation
        self.changes = []
        # TODO will need a proper way to measure this
        self.similarity_threshold = 1

    def compare_block_defs(self):
        has_diff = self._compare_block_defs(
            self.old_streamblock_def, self.new_streamblock_def
        )
        if has_diff:
            for change in self.changes:
                print(change)

    def _compare_block_defs(self, old_block_def, new_block_def, parent_path=""):
        """TODO description

        For now we do 2 things here,
        1. For each old child block, try to find if there is a new child block that it will be
        mapped to. If found and requires a rename operation, keep track of that. If not found and
        requires a remove operation, keep track of that.
        2. Repeat 1 for each (nested) child block (if any) of the mapped child block.

        When doing 1, if we can't find a mapping with the same name and structure, we will need to
        go through new child blocks, and if they are considerably similar, ask the user whether the
        block was renamed. When checking similarity, we will need to consider name, args (from
        deconstruct) and children/structure.
        """

        # TODO see if we can do a bottom up approach here:
        #   Problem with a bottom up approach is that if we don't know what parent blocks are going
        #   to be mapped, then we can't figure out what the possible child blocks are that a given
        #   block can map to.
        # TODO see if there's another way to avoid recursing through child blocks in 2 separate
        #   places (in the recursion itself and when comparing). Also see if it's even needed to
        #   check all nested children or only the direct children would be okay.
        # TODO see if there are any algorithms for this kind of thing

        if hasattr(old_block_def, "child_blocks"):
            # for StreamBlocks and StructBlocks
            old_child_defs = old_block_def.child_blocks
            new_child_defs = new_block_def.child_blocks
        elif hasattr(old_block_def, "child_block"):
            # ListBlocks have a single `.child_block`
            old_child_defs = {"item": old_block_def.child_block}
            new_child_defs = {"item": new_block_def.child_block}
        else:
            # Non Structural Blocks don't have children
            # TODO figure out what we need to check for these
            return False

        # just a value to keep track of whether we have any mappings we require an operation for at
        # any point in the recursion tree
        has_diff = False

        # To keep track of the block path. We will need this for creating operations
        path_suffix = "" if parent_path == "" else "."

        old_child_names = set(old_child_defs.keys())
        new_child_names = set(new_child_defs.keys())
        # child names that are exclusive to the new children
        new_only_child_names = new_child_names - old_child_names

        for old_child_name in old_child_names:
            old_child_path = parent_path + path_suffix + old_child_name
            old_child_def = old_child_defs[old_child_name]
            is_child_mapped = False

            # For now assume that same name means same block (i.e. the old block wasn't deleted
            # and a new block with the same name added)
            # TODO compare name, args and child structure here too
            if old_child_name in new_child_names:
                new_child_def = new_child_defs[old_child_name]
                # recursion call
                has_diff = has_diff or self._compare_block_defs(
                    old_child_def,
                    new_child_def,
                    old_child_path,
                )
                is_child_mapped = True

            else:
                # Find out if the block maps to one of the other new children
                for new_only_child_name in new_only_child_names:
                    new_child_def = new_child_defs[new_only_child_name]
                    # compare the blocks and get their similarity
                    similarity = self.get_block_similarity(
                        old_child_def,
                        new_child_def,
                    )
                    # TODO make a proper way to compare similarity
                    if similarity >= self.similarity_threshold:
                        # TODO how django asks the questions in makemigrations
                        is_renamed = (
                            input(
                                "'"
                                + old_child_path
                                + "' renamed to '"
                                + new_only_child_name
                                + "'"
                                + "? y/n"
                            )
                            == "y"
                        )
                        if is_renamed:
                            is_child_mapped = True
                            # keep parent block defs here to determine operation
                            self.changes.append(
                                (
                                    old_child_path,
                                    new_only_child_name,
                                    old_block_def,
                                    new_block_def,
                                )
                            )
                            new_only_child_names.remove(new_only_child_name)
                            has_diff = True
                            # TODO do we call the recursive compare here?
                            break

            # if there is no block to map this to, check if it has been removed
            if not is_child_mapped:
                is_removed = input("'" + old_child_path + "' removed? y/n") == "y"
                if is_removed:
                    has_diff = True
                    self.changes.append((old_child_path, None, old_block_def, None))

        return has_diff

    def get_block_similarity(self, old_block_def, new_block_def):
        # TODO this is temporary, need a proper way to measure similarity
        similarity = 0

        similarity += self.get_block_arg_similarity(old_block_def, new_block_def)

        similarity += self.get_block_structure_similarity(old_block_def, new_block_def)

        return similarity

    def get_block_arg_similarity(self, old_block_def, new_block_def):
        # TODO
        # breakpoint()

        similarity = 0
        old_path, old_args, old_kwargs = old_block_def.deconstruct()
        new_path, new_args, new_kwargs = new_block_def.deconstruct()

        if old_path == new_path:
            similarity += 1

        temp = 0
        for arg in old_args:
            if arg in new_args:
                temp += 1
        if temp > 0:
            similarity += temp / len(old_args)
        # TODO kwargs

        return similarity

    def get_block_structure_similarity(self, old_block_def, new_block_def):
        # TODO
        # breakpoint()
        return 0
