.PHONY: generate-docs
.DEFAULT_GOAL := help

help:		## ⁉️  - Display help comments for each make command
	@grep -E '^[0-9a-zA-Z_-]+:.*? .*$$'  \
		$(MAKEFILE_LIST)  \
		| awk 'BEGIN { FS=":.*?## " }; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'  \
		| sort

generate-docs:		# generate reference docs in docs/REFERENCE.md
	pydoc-markdown -I . \
		-m wagtail_streamfield_migration_toolkit.migrate_operation \
		-m wagtail_streamfield_migration_toolkit.operations \
		-m wagtail_streamfield_migration_toolkit.utils \
		--render-toc > docs/REFERENCE.md