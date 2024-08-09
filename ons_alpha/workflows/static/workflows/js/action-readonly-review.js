function initReviewButton() {
    let reviewButton = document.querySelector('button[name="action-readonly-review"]');
    if (!reviewButton) {
        return;
    }

    const target = reviewButton.parentElement.querySelector('button[data-w-dropdown-target="toggle"]');
    if (!target) {
        return;
    }
    reviewButton.addEventListener('click', function (event) {
        target.click();
        event.preventDefault();
    });
}

// Function to find the React internal instance
function getReactInternalInstance(element) {
    return Object.keys(element).find(key =>
        key.startsWith('__reactInternalInstance$')
    );
}

function preventContentChanges(editorInstance) {
    let originalContent = editorInstance.getEditorState().getCurrentContent();
    const originalOnChange = editorInstance.onChange;

    editorInstance.onChange = (editorState) => {
        if (editorState.getCurrentContent() !== originalContent) {
            if (editorState.getLastChangeType() === "change-inline-style") {
                originalOnChange(editorState);
                originalContent = editorState.getCurrentContent();
            }
            else {
                // preserve selection
                const state = DraftJS.EditorState.set(
                    DraftJS.EditorState.createWithContent(originalContent, editorState.getDecorator()),
                    {
                        selection: editorState.getSelection(),
                        undoStack: editorState.getUndoStack(),
                        redoStack: editorState.getRedoStack(),
                        inlineStyleOverride: editorState.getInlineStyleOverride(),
                    },
                );
                return originalOnChange(DraftJS.EditorState.acceptSelection(state, state.getSelection()));
            }
        }
        else {
            return originalOnChange(editorState);
        }
    };
}

function initializeReadOnlyDraftail() {
    const possibleEditors = document.querySelectorAll('[data-draftail-editor]');
    possibleEditors.forEach(element => {
        // This is likely a Draft.js editor
        const internalInstance = getReactInternalInstance(element);
        if (internalInstance) {
            const editor = element[internalInstance].return.stateNode;
            if (editor && typeof editor.getEditorState === 'function') {
                // Confirm it's a Draft.js editor and make it read-only
                preventContentChanges(editor);
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.body.classList.contains("ons-readonly")) {
        initReviewButton();
        initializeReadOnlyDraftail();
    }
});
