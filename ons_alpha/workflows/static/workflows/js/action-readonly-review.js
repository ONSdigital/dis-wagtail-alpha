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
  const currentContent = editorInstance.getEditorState().getCurrentContent();
  const originalOnChange = editorInstance.onChange;

  editorInstance.onChange = (editorState) => {
    if (editorState.getCurrentContent() !== currentContent) {
      // Prevent content changes by reverting to the original content
      return originalOnChange(DraftJS.EditorState.undo(editorState));
    }

    // Allow selection changes
    return originalOnChange(editorState);
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
    initReviewButton();
    initializeReadOnlyDraftail();
});
