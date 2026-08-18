// ============================================================================
// core/permissions.js — Role-Based Access Control (RBAC)
// Manages user permissions and navigation visibility
// ============================================================================

// Get current user's permissions based on role
window.getPermissions = function () {
  const role = localStorage.getItem("admin_role");
  if (role === "super_admin") {
    // Super admin has all permissions (hardcoded)
    return {
      dashboard: ["view"],
      users: ["view", "create", "edit", "delete"],
      distributors: ["view", "create", "edit", "delete"],
      staff: ["view", "create", "edit", "delete"],
      products: ["view", "create", "edit", "delete"],
      orders: ["view", "create", "edit", "delete"],
      queries: ["view", "create", "edit", "delete"],
    };
  }
  // For admin/sub_admin: parse stored permissions JSON from localStorage
  const userJson = localStorage.getItem("admin_user");
  if (userJson) {
    const user = JSON.parse(userJson);
    if (user.permissions) {
      try {
        return JSON.parse(user.permissions);
      } catch (e) {}
    }
  }
  return {}; // No permissions by default
};

// Check if current user has a specific permission
window.hasPermission = function (module, action) {
  if (module === "dashboard" && action === "view") return true; // always allowed
  const perms = window.getPermissions();
  return perms[module] && perms[module].includes(action);
};

// Apply permissions to sidebar navigation — show/hide items based on access
function applyPermissionNav() {
  const role = localStorage.getItem("admin_role");

  // Sidebar nav items
  const navDash = document.getElementById("nav-dashboard-view");
  const navUsers = document.getElementById("nav-users-view");
  const navAdminStaff = document.getElementById("nav-admin-staff-view");
  const navDistributors = document.getElementById("nav-distributors-view");
  const navStaff = document.getElementById("nav-create-staff-view");
  const navProducts = document.getElementById("nav-products-view");
  const navCreateProduct = document.getElementById("nav-create-product-view");
  const navOrders = document.getElementById("nav-orders-view");
  const navQueries = document.getElementById("nav-queries-view");

  if (navDash) navDash.style.display = hasPermission("dashboard", "view") ? "flex" : "none";
  if (navUsers) navUsers.style.display = hasPermission("users", "view") ? "flex" : "none";
  if (navAdminStaff) navAdminStaff.style.display = hasPermission("staff", "view") ? "flex" : "none";
  if (navDistributors) navDistributors.style.display = hasPermission("distributors", "view") ? "flex" : "none";
  if (navStaff) navStaff.style.display = hasPermission("staff", "create") ? "flex" : "none";
  if (navProducts) navProducts.style.display = hasPermission("products", "view") ? "flex" : "none";
  if (navCreateProduct) navCreateProduct.style.display = hasPermission("products", "create") ? "flex" : "none";
  if (navOrders) navOrders.style.display = hasPermission("orders", "view") ? "flex" : "none";
  if (navQueries) navQueries.style.display = hasPermission("queries", "view") ? "flex" : "none";

  // Create buttons in tables — show/hide based on create permission
  const btnCreateStaff = document.getElementById("btn-create-staff");
  if (btnCreateStaff) btnCreateStaff.style.display = hasPermission("staff", "create") ? "inline-block" : "none";

  const btnCreateUser = document.getElementById("btn-create-user");
  if (btnCreateUser) btnCreateUser.style.display = hasPermission("users", "create") ? "inline-block" : "none";

  const btnCreateDist = document.getElementById("btn-create-distributor");
  if (btnCreateDist) btnCreateDist.style.display = hasPermission("distributors", "create") ? "inline-block" : "none";

  const btnCreateProduct = document.getElementById("btn-create-product");
  if (btnCreateProduct) btnCreateProduct.style.display = hasPermission("products", "create") ? "flex" : "none";

  // Route to correct tab from URL path
  routeFromPath();

  // If no tab is active, navigate to first accessible tab
  if (!document.querySelector(".panel-page.active")) {
    if (hasPermission("dashboard", "view")) switchTab("dashboard-view");
    else if (hasPermission("users", "view")) switchTab("users-view");
    else if (hasPermission("staff", "view")) switchTab("admin-staff-view");
    else if (hasPermission("distributors", "view")) switchTab("distributors-view");
    else if (hasPermission("products", "view")) switchTab("products-view");
    else if (hasPermission("orders", "view")) switchTab("orders-view");
    else if (hasPermission("queries", "view")) switchTab("queries-view");
  }
}

// Show access-denied modal with lock icon and animated overlay
function showAuthModal(title, message) {
  const overlay = document.createElement("div");
  overlay.style.position = "fixed";
  overlay.style.inset = "0";
  overlay.style.background = "rgba(15, 23, 42, 0.7)";
  overlay.style.backdropFilter = "blur(10px)";
  overlay.style.display = "flex";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.zIndex = "99999";
  overlay.style.opacity = "0";
  overlay.style.transition = "opacity 0.3s ease";

  const modal = document.createElement("div");
  modal.style.background = "#ffffff";
  modal.style.borderRadius = "20px";
  modal.style.padding = "32px 40px";
  modal.style.maxWidth = "400px";
  modal.style.width = "90%";
  modal.style.boxShadow = "0 25px 50px -12px rgba(0, 0, 0, 0.25)";
  modal.style.textAlign = "center";
  modal.style.transform = "translateY(20px) scale(0.95)";
  modal.style.transition = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";

  modal.innerHTML = `
    <div style="width: 60px; height: 60px; background: rgba(239, 68, 68, 0.1); color: #ef4444; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto 20px;">
      <i class="fa-solid fa-user-lock"></i>
    </div>
    <h3 style="font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 12px; letter-spacing: -0.5px;">${title}</h3>
    <p style="font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 24px;">${message}</p>
    <button id="auth-modal-btn" style="background: linear-gradient(120deg, #ef4444, #dc2626); color: white; border: none; padding: 12px 24px; border-radius: 12px; font-size: 14px; font-weight: 600; cursor: pointer; width: 100%; transition: opacity 0.2s;">Understood</button>
  `;

  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  requestAnimationFrame(() => {
    overlay.style.opacity = "1";
    modal.style.transform = "translateY(0) scale(1)";
  });

  document.getElementById("auth-modal-btn").addEventListener("click", () => {
    overlay.style.opacity = "0";
    modal.style.transform = "translateY(20px) scale(0.95)";
    setTimeout(() => overlay.remove(), 300);
  });
}
