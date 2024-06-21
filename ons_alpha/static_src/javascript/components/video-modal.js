// Simple video modal using <dialog>

// Assumes a structure as follows
// <div data-video-modal>
//     <button data-modal-open>Open video</button>
//     <dialog data-modal-window>
//         Video embed
//         <button data-modal-close>Close</button>
//     </dialog>
// </div>

class VideoModal {
    static selector() {
        return '[data-video-modal]';
    }

    constructor(node) {
        this.modal = node;
        this.modalOpen = this.modal.querySelector('[data-modal-open]');
        this.modalWindow = this.modal.querySelector('[data-modal-window]');
        this.modalClose = this.modal.querySelector('[data-modal-close]');
        this.iframe = this.modal.querySelector('iframe');
        this.src = this.iframe.getAttribute('src');
        this.bindEvents();
    }

    // Toggle the iframe's src as required
    setIframeSrc(setSrc) {
        if (setSrc === true) {
            if (!this.iframe.getAttribute('src').length) {
                this.iframe.setAttribute('src', this.src);
            }
        } else {
            this.iframe.setAttribute('src', '');
        }
    }

    openModal() {
        if (typeof this.modalWindow.showModal === 'function') {
            this.modalWindow.showModal();
            this.setIframeSrc(true);
        }
    }

    closeModal() {
        this.modalWindow.close();
        this.setIframeSrc(false);
    }

    clickOutsideToCloseModal(e) {
        const rect = this.modalWindow.getBoundingClientRect();
        if (
            e.clientY < rect.top ||
            e.clientY > rect.bottom ||
            e.clientX < rect.left ||
            e.clientX > rect.right
        ) {
            this.modalWindow.close();
            this.setIframeSrc(false);
        }
    }

    bindEvents() {
        this.modalOpen.addEventListener('click', () => {
            this.openModal();
        });

        this.modalClose.addEventListener('click', () => {
            this.closeModal();
        });

        this.modalWindow.addEventListener('click', (e) => {
            this.clickOutsideToCloseModal(e);
        });
    }
}

export default VideoModal;
