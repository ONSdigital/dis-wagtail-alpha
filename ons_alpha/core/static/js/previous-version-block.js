/* global $ */

class PreviousVersionBlock {
    constructor(blockDef, placeholder, prefix, initialState) {
        this.blockDef = blockDef;
        this.element = document.createElement('div');

        placeholder.replaceWith(this.element);

        this.renderContent(initialState);
    }

    renderContent(state) {
        if (state) {
            this.element.innerHTML = `
                <a class="button button-small button-secondary" href="../revisions/${state}/view/">View revision</a>
                <a class="button button-small button-secondary" href="../revisions/${state}/revert/">Review revision</a>
            `;
        } else {
            this.element.innerHTML = `
                <p>The previous version will be automatically chosen when this page is saved.</p>
            `;
        }
    }

    setState(state) {
        this.renderContent(state);
    }

    setError(_errorList) {}

    getState() {
        return null;
    }

    getValue() {
        return null;
    }

    focus() {}
}

class PrevionsVersionBlockDefinition extends window.wagtailStreamField.blocks.FieldBlockDefinition {
    render(placeholder, prefix, initialState) {
        return new PreviousVersionBlock(this, placeholder, prefix, initialState);
    }
}

window.telepath.register("ons_alpha.core.blocks.panels.PreviousVersionBlock", PrevionsVersionBlockDefinition);
