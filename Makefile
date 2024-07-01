DESIGN_SYSTEM_VERSION=`cat .design-system-version`

.DEFAULT_GOAL := help

.PHONY: help load-design-system-templates

help:  ## ⁉️   - Display help comments for each make command
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_\-\.]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)


load-design-system-templates:  ## 🎨️   - Load the design system templates
	./scripts/load_release.sh onsdigital/design-system $(DESIGN_SYSTEM_VERSION)
	./scripts/finalize_design_system_setup.sh $(DESIGN_SYSTEM_VERSION)
