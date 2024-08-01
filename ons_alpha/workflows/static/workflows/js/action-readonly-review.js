document.addEventListener('DOMContentLoaded', function() {
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
});
