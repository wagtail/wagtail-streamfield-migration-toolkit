from django.db.migrations.questioner import InteractiveMigrationQuestioner


# TODO determine if we write our own. We won't be using most of the methods in this
class InteractiveDataMigrationQuestioner(InteractiveMigrationQuestioner):
    def ask_block_rename(self, old_path, new_path):
        msg = "Was '{}' renamed to '{}' ? [y/N]"
        return self._boolean_input(msg.format(old_path, new_path))

    def ask_block_remove(self, old_path):
        msg = "Was '{}' removed? [y/N]"
        return self._boolean_input(msg.format(old_path))
