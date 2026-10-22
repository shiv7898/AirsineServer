// ============================================================================
// core/utils.js — Global UI Utilities & Authentication Guard
// Toast notifications, Loading spinner, and Automatic Token Checks
// ============================================================================

// Toast Helper — success/error notification popup
function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  const icon = document.getElementById("toast-icon");
  const msg = document.getElementById("toast-msg");

  if (!toast || !icon || !msg) return;

  msg.textContent = message;
  toast.className = `toast show ${type}`;

  if (type === "success") {
    icon.className = "fa-solid fa-circle-check";
  } else {
    icon.className = "fa-solid fa-triangle-exclamation";
  }

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

// Loader Helper — show/hide loading spinner
function toggleLoader(show) {
  const loader = document.getElementById("loader");
  if (loader) {
    loader.style.display = show ? "flex" : "none";
  }
}

// Global Auth Guard: Retrieve token or redirect to Login if missing on protected actions
function getAuthToken(redirectIfMissing = true) {
  const token = localStorage.getItem("admin_token");
  if (!token) {
    if (redirectIfMissing) {
      if (typeof showLoginPage === "function") {
        showLoginPage();
      } else if (typeof window.showLoginPage === "function") {
        window.showLoginPage();
      }
    }
    return null;
  }
  return token;
}

// Handle session expiration cleanly
function handleSessionExpired() {
  localStorage.removeItem("admin_token");
  localStorage.removeItem("admin_user");
  localStorage.removeItem("admin_role");
  showToast("Session expired. Please log in again.", "error");
  if (typeof showLoginPage === "function") {
    showLoginPage();
  } else if (typeof window.showLoginPage === "function") {
    window.showLoginPage();
  }
}

// Global Fetch Interceptor: Catch 401/403 on protected API calls and redirect to login
if (typeof window !== "undefined" && window.fetch) {
  const originalFetch = window.fetch;
  window.fetch = async function (...args) {
    const response = await originalFetch.apply(this, args);

    const url =
      typeof args[0] === "string"
        ? args[0]
        : args[0] && args[0].url
        ? args[0].url
        : "";

    // Ignore public auth routes (login, forgot-password, etc.)
    const isPublicAuthRoute =
      url.includes("/login") ||
      url.includes("/forgot-password") ||
      url.includes("/verify-otp") ||
      url.includes("/reset-password") ||
      url.includes("/resend-otp");

    if ((response.status === 401 || response.status === 403) && !isPublicAuthRoute) {
      console.warn("Protected API rejected with 401/403. Redirecting to login:", url);
      handleSessionExpired();
    }

    return response;
  };
}

// Expose globally
window.showToast = showToast;
window.toggleLoader = toggleLoader;
window.getAuthToken = getAuthToken;
window.handleSessionExpired = handleSessionExpired;
