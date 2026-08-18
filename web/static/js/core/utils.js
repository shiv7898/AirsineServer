// ============================================================================
// core/utils.js — Global UI Utilities
// Toast notifications & Loading spinner helpers
// ============================================================================

// Toast Helper — success/error notification popup
function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  const icon = document.getElementById("toast-icon");
  const msg = document.getElementById("toast-msg");

  msg.textContent = message;
  toast.className = `toast show ${type}`;

  if (type === "success") {
    icon.className = "fa-solid fa-circle-check";
  } else {
    icon.className = "fa-solid fa-triangle-exclamation";
  }

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// Loader Helper — show/hide loading spinner
function toggleLoader(show) {
  document.getElementById("loader").style.display = show ? "flex" : "none";
}
