// ============================================================================
// core/init.js — App Initialization, Routing & UI Layout
// Handles page startup, login/dashboard switching, sidebar, and profile UI
// ============================================================================

// On page load: check token and show correct page
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("admin_token");
  if (token) {
    // Backfill admin_role from JWT payload if missing (old sessions)
    if (!localStorage.getItem("admin_role")) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        if (payload.role) localStorage.setItem("admin_role", payload.role);
      } catch (e) {}
    }
    showDashboard();
  } else {
    showLoginPage();
  }
});

// Show Login page, hide Dashboard
function showLoginPage() {
  document.getElementById("auth-page").style.display = "flex";
  document.getElementById("dashboard-page").style.display = "none";
  if (window.location.pathname !== "/login") {
    history.pushState(null, "", "/login");
  }
}

// Show Dashboard, fill user info in sidebar/header/profile
function showDashboard() {
  document.getElementById("auth-page").style.display = "none";
  const dash = document.getElementById("dashboard-page");
  dash.style.display = "flex";
  dash.style.flexDirection = "row";
  dash.style.height = "100vh";
  dash.style.overflow = "hidden";

  // Populate user info from localStorage
  const userJson = localStorage.getItem("admin_user");
  if (userJson) {
    const user = JSON.parse(userJson);

    // Header & Sidebar name/initials
    document.getElementById("user-display-name").textContent = user.name || "Admin";
    document.getElementById("user-initials").textContent = (user.name || "AD")
      .split(" ")
      .map((n) => n[0])
      .join("")
      .substring(0, 2)
      .toUpperCase();

    // Sidebar logo area
    const logoEmail = document.getElementById("sidebar-logo-email");
    if (logoEmail) logoEmail.textContent = user.email || "admin@airsine.com";
    const headerEmail = document.getElementById("header-user-email");
    if (headerEmail) headerEmail.textContent = user.email || "admin@airsine.com";
    const dropdownName = document.getElementById("dropdown-user-name");
    if (dropdownName) dropdownName.textContent = user.name || "Admin";

    // Role badge in sidebar and header
    const logoRole = document.getElementById("sidebar-logo-role");
    const headerRole = document.getElementById("header-user-role");
    if (logoRole || headerRole) {
      const actualRole = localStorage.getItem("admin_role") || user.role || "N/A";
      const roleText = actualRole.replace("_", " ").toUpperCase();
      if (logoRole) logoRole.textContent = roleText;
      if (headerRole)
        headerRole.textContent = actualRole
          .replace("_", " ")
          .replace(/\b\w/g, (l) => l.toUpperCase());

      const profBadge = document.getElementById("prof-role-badge");
      if (profBadge) profBadge.textContent = roleText;
    }

    const logoId = document.getElementById("sidebar-logo-id");
    if (logoId) logoId.textContent = user.custom_id || "ID-N/A";

    // Profile page details
    const profAvatar = document.getElementById("prof-avatar");
    if (profAvatar)
      profAvatar.textContent = (user.name || "AD")
        .split(" ")
        .map((n) => n[0])
        .join("")
        .substring(0, 2)
        .toUpperCase();

    const profName = document.getElementById("prof-name-large");
    if (profName) profName.textContent = user.name || "User Name";

    const profCustomId = document.getElementById("prof-custom-id");
    if (profCustomId) profCustomId.textContent = user.custom_id || "N/A";

    const profEmail = document.getElementById("prof-email");
    if (profEmail) profEmail.textContent = user.email || "N/A";

    const profPhone = document.getElementById("prof-phone");
    if (profPhone) profPhone.textContent = user.phone || "N/A";

    const profGender = document.getElementById("prof-gender");
    if (profGender) {
      const age = user.age ? user.age + " Yrs" : "";
      const gender = user.gender ? user.gender : "";
      profGender.textContent =
        age && gender ? `${age} / ${gender}` : age || gender || "N/A";
    }

    const profAddressHome = document.getElementById("prof-address-home");
    if (profAddressHome) profAddressHome.textContent = user.homeAddress || "-";

    const profAddressArea = document.getElementById("prof-address-area");
    if (profAddressArea) profAddressArea.textContent = user.area || "-";

    const profAddressDistrict = document.getElementById("prof-address-district");
    if (profAddressDistrict) profAddressDistrict.textContent = user.district || "-";

    const profAddressState = document.getElementById("prof-address-state");
    if (profAddressState) profAddressState.textContent = user.state || "-";

    const profAddressPincode = document.getElementById("prof-address-pincode");
    if (profAddressPincode) profAddressPincode.textContent = user.pincode || "-";
  }

  applyPermissionNav();

  // Route to correct tab based on URL or default to dashboard
  if (
    window.location.pathname === "/login" ||
    window.location.pathname === "/"
  ) {
    switchTab("dashboard-view");
  } else {
    routeFromPath();
    setTimeout(() => {
      if (!document.querySelector(".panel-page.active")) {
        switchTab("dashboard-view");
      }
    }, 10);
  }
}

// ============================================================================
// Sidebar Controls
// ============================================================================

// Mobile: toggle sidebar open/close with overlay
function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  sidebar.classList.toggle("open");
  overlay.classList.toggle("show");
}

// Mobile: force close sidebar
function closeSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  if (sidebar) sidebar.classList.remove("open");
  if (overlay) overlay.classList.remove("show");
}

// Desktop: collapse/expand sidebar with smooth chart resize
function toggleSidebarDesktop() {
  const sidebar = document.querySelector(".sidebar");
  if (sidebar) {
    sidebar.classList.toggle("collapsed");

    // Animate chart resize during transition
    let count = 0;
    const interval = setInterval(() => {
      if (window.rolesChartInstance) window.rolesChartInstance.resize();
      count++;
      if (count >= 15) clearInterval(interval);
    }, 20);

    setTimeout(() => {
      window.dispatchEvent(new Event("resize"));
      if (window.rolesChartInstance) window.rolesChartInstance.resize();
    }, 310);
  }
}

// ============================================================================
// Profile Dropdown
// ============================================================================

// Toggle profile dropdown menu visibility
function toggleProfileDropdown() {
  const dropdown = document.getElementById("profile-dropdown");
  if (dropdown) dropdown.classList.toggle("show");
}

// Close profile dropdown when clicking outside
document.addEventListener("click", (e) => {
  const profile = document.querySelector(".header-profile");
  const dropdown = document.getElementById("profile-dropdown");
  if (profile && dropdown) {
    if (!profile.contains(e.target)) {
      dropdown.classList.remove("show");
    }
  }
});
