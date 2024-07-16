window.addEventListener("DOMContentLoaded", function() {
    const expandablePanels = document.querySelectorAll(".w-panel[data-auto-expand]");

    expandablePanels.forEach(function(panel) {
        const blockCount = parseInt(panel.querySelector("[data-streamfield-stream-count").value);
        if (blockCount !== 0) {
            // If there are already blocks, don't try and insert any
            return;
        }

        const addButton = panel.querySelector(".c-sf-add-button");
        if (addButton.disabled) {
            // If the add button is disabled, no more blocks can be added
            return;
        }

        addButton.click();
    });
});
