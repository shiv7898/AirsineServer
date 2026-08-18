// ============================================================================
// core/uiComponents.js
// Shared UI functions and listeners (Modals, Image Viewer, Header Scroll, Auth UI)
// ============================================================================

// ----------------------------------------------------------------------------
// Generic Modal Helper
// ----------------------------------------------------------------------------
window.closeModal = function(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.style.display = 'none';
    // Only push state for user modals if needed, to avoid breaking query view
    if (modalId === 'view-user-modal' || modalId === 'edit-user-modal') {
        history.pushState(null, '', '/users');
    }
};

// ----------------------------------------------------------------------------
// Image Viewer Modal Logic
// ----------------------------------------------------------------------------
window.currentImageIndex = 0;
window.currentImagesArray = [];

window.viewQueryImage = function(imageString) {
    window.currentImagesArray = imageString.split(',');
    window.currentImageIndex = 0;
    window.updateImageDisplay();
    const modal = document.getElementById('image-viewer-modal');
    if (modal) modal.style.display = 'flex';
};

window.updateImageDisplay = function() {
    const img = document.getElementById('query-image-display');
    if (!img) return;
    
    img.src = '/uploads/support/' + window.currentImagesArray[window.currentImageIndex];
    
    const counter = document.getElementById('image-counter');
    if (counter) {
        if (window.currentImagesArray.length > 1) {
            counter.style.display = 'block';
            counter.innerText = `${window.currentImageIndex + 1} / ${window.currentImagesArray.length}`;
        } else {
            counter.style.display = 'none';
        }
    }

    const prevBtn = document.getElementById('prev-img-btn');
    const nextBtn = document.getElementById('next-img-btn');
    if (prevBtn) prevBtn.style.display = window.currentImagesArray.length > 1 ? 'flex' : 'none';
    if (nextBtn) nextBtn.style.display = window.currentImagesArray.length > 1 ? 'flex' : 'none';
};

window.nextImage = function() {
    if (window.currentImageIndex < window.currentImagesArray.length - 1) {
        window.currentImageIndex++;
    } else {
        window.currentImageIndex = 0; // wrap
    }
    window.updateImageDisplay();
};

window.prevImage = function() {
    if (window.currentImageIndex > 0) {
        window.currentImageIndex--;
    } else {
        window.currentImageIndex = window.currentImagesArray.length - 1; // wrap
    }
    window.updateImageDisplay();
};

// ----------------------------------------------------------------------------
// Auth / Logout
// ----------------------------------------------------------------------------
window.handleLogout = function() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    localStorage.removeItem('admin_role');
    if (window.showToast) window.showToast('Logged out successfully');
    if (window.showLoginPage) window.showLoginPage();
};

// ----------------------------------------------------------------------------
// Header Scroll Animation
// ----------------------------------------------------------------------------
let lastScrollTop = 0;
let currentScrollContainer = null;
let isHeaderAnimating = false;

window.attachScrollListener = function(tabId) {
    const topHeader = document.querySelector('.top-header');
    if (!topHeader) return;
    
    if(currentScrollContainer) {
        currentScrollContainer.removeEventListener('scroll', window.handleHeaderScroll);
    }
    topHeader.classList.remove('hidden-scroll'); // Reset when changing tabs
    lastScrollTop = 0;

    if(tabId === 'dashboard-view') return; // Do not apply on dashboard

    const el = document.getElementById(tabId);
    if(!el) return;

    // Do not apply header hide on table scrolls
    if (el.querySelector('.table-container')) return;

    // Find the scrollable container inside this tab
    currentScrollContainer = null;
    if (!currentScrollContainer) {
        // Fallback: check direct children for computed overflow-y
        const children = el.children;
        for (let i = 0; i < children.length; i++) {
            const style = window.getComputedStyle(children[i]);
            if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
                currentScrollContainer = children[i];
                break;
            }
        }
    }
    if (!currentScrollContainer) {
        currentScrollContainer = el;
    }
    if(currentScrollContainer) {
        currentScrollContainer.addEventListener('scroll', window.handleHeaderScroll);
    }
};

window.handleHeaderScroll = function(e) {
    if (isHeaderAnimating) return;
    
    const topHeader = document.querySelector('.top-header');
    if (!topHeader) return;
    
    const st = e.target.scrollTop;
    const delta = Math.abs(lastScrollTop - st);
    
    // Only trigger if scrolled more than 5px to prevent jitter
    if (delta <= 5) return;
    
    if (st > lastScrollTop && st > 60) {
        // Scrolling DOWN -> HIDE Header
        if (!topHeader.classList.contains('hidden-scroll')) {
            topHeader.classList.add('hidden-scroll');
            isHeaderAnimating = true;
            setTimeout(() => isHeaderAnimating = false, 400);
        }
    } else if (st < lastScrollTop) {
        // Scrolling UP -> SHOW Header
        if (topHeader.classList.contains('hidden-scroll')) {
            topHeader.classList.remove('hidden-scroll');
            isHeaderAnimating = true;
            setTimeout(() => isHeaderAnimating = false, 400);
        }
    }
    
    lastScrollTop = st <= 0 ? 0 : st;
};

// ----------------------------------------------------------------------------
// Misc UI Initializations
// ----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    // Password Hide/Show Logic
    const togglePwdBtn = document.querySelector('.show-pwd');
    const pwdInput = document.getElementById('login-password');
    if(togglePwdBtn && pwdInput) {
        togglePwdBtn.addEventListener('click', () => {
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
                togglePwdBtn.textContent = 'HIDE';
            } else {
                pwdInput.type = 'password';
                togglePwdBtn.textContent = 'SHOW';
            }
        });
    }
    
    // Restore last used Product Type and Tax/GST
    const savedGst = localStorage.getItem('last_product_gst');
    if (savedGst) {
        const cpGst = document.getElementById('cp-gst');
        if (cpGst) cpGst.value = savedGst;
    }
    const savedType = localStorage.getItem('last_product_type');
    if (savedType) {
        const cpType = document.getElementById('cp-type');
        if (cpType) cpType.value = savedType;
    }
});
