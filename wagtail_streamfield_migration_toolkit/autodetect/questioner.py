from django.db.migrations.questioner import InteractiveMigrationQuestioner


# TODO determine if we write our own. We won't be using most of the methods in this
class InteractiveDataMigrationQuestioner(InteractiveMigrationQuestioner):
    def ask_if_block_renamed(self, old_path, new_path):
        msg = "Was '{}' renamed to '{}' ? [y/N]"
        return self._boolean_input(msg.format(old_path, new_path))

    def ask_if_block_removed(self, old_path):
        msg = "Was '{}' removed? [y/N]"
        return self._boolean_input(msg.format(old_path))

    def ask_if_block_same(self, old_path, new_path):
        msg = "Found blocks '{}' and '{}' with minor differences. Is this the same block? [y/N]"
        return self._boolean_input(msg.format(old_path, new_path))
