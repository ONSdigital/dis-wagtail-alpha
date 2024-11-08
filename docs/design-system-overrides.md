# Design System and Overrides

The site front-end code extends the [ONS Design system](https://service-manual.ons.gov.uk/design-system/). We extend the [base template](https://service-manual.ons.gov.uk/design-system/foundations/base-page-template) and make use of design system utility classes, colours and typography.

## Overrides

For the November prototype, in order to incorporate some new design elements, some parts of the design system had to be overridden, both HTML markup and styling.

### Markup overrides

In some cases it was necessary to duplicate and make changes to the nunjucks templates in the design system. These can be found in the `ons_alpha/jinja2/component_overrides` folder. Each component includes comments as to what has changed.

The base page template (`ons_alpha/jinja2/templates/base_page.html`) has some important changes to the `pageContent` block in order to add the full width section for the new header areas - including relocating the `<main>` tag so that the new header area is nested inside it.

### Styling overrides

In some cases we needed to extend or override design system styling. These changes can be found in `ons_alpha/static_src/sass/components/design_system_overrides`.

## New markup and styling

### Markup for new components

Note that new markup can be found in the page templates for the topic, bulletin and information pages. These can be found in the `ons_alpha/jinja2/templates/pages` folder. Where new components are part of re-orderable streamfield blocks, they can be found in the `ons_alpha/jinja2/templates/components/streamfield` folder.

### Styling for new components

Styling for new components can be found in `ons_alpha/static_src/sass/components/`.

## Incorporation of new components into the design system

For beta, the plan is to incorporate the customisations made for the November prototype into the design system, so that they can be used without the need to duplicate and / or override code.
