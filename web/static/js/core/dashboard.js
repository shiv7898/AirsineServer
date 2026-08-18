// ============================================================================
// core/dashboard.js — Dashboard Data & Charts
// Fetches stats from API and renders Chart.js charts
// ============================================================================

let rolesChart = null;

// Fetch dashboard stats from API and populate UI cards
async function refreshDashboardData() {
  const token = localStorage.getItem("admin_token");
  if (!token) return;

  toggleLoader(true);
  try {
    const response = await fetch(API_ENDPOINTS.DASHBOARD, {
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = await response.json();
    toggleLoader(false);

    if (!response.ok)
      throw new Error(data.detail || "Failed to fetch dashboard data");

    // Populate stat cards
    document.getElementById("stat-patients").textContent = data.users.total_patients;
    document.getElementById("stat-doctors").textContent = data.users.total_doctors;
    document.getElementById("stat-distributors").textContent = data.users.total_distributors;

    // Staff = admin + sub_admin + super_admin combined count
    const staffCount =
      (data.users.total_admins || 0) +
      (data.users.total_sub_admins || 0) +
      (data.users.total_super_admins || 0);
    document.getElementById("stat-staff").textContent = staffCount;

    document.getElementById("stat-orders-total").textContent = data.orders.total_orders;
    document.getElementById("stat-products").textContent = data.products.total_products;

    const patProdEl = document.getElementById("stat-pat-products");
    if (patProdEl) patProdEl.textContent = data.products.patient_products || 0;

    const distProdEl = document.getElementById("stat-dist-products");
    if (distProdEl) distProdEl.textContent = data.products.distributor_products || 0;

    document.getElementById("stat-revenue").textContent =
      `₹${data.revenue.total_revenue.toLocaleString("en-IN")}`;

    // Render charts
    setupRolesChart(data.users);
    setupWeeklyCharts(data.weekly_stats);
  } catch (err) {
    toggleLoader(false);
    showToast(err.message, "error");
  }
}

// Doughnut chart — Role-wise user distribution
function setupRolesChart(userStats) {
  const ctx = document.getElementById("rolesChart").getContext("2d");

  if (window.rolesChartInstance) {
    window.rolesChartInstance.destroy();
  }

  window.rolesChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Patients", "Doctors", "Distributors", "Admins", "Sub Admins", "Super Admins"],
      datasets: [
        {
          data: [
            userStats.total_patients || 0,
            userStats.total_doctors || 0,
            userStats.total_distributors || 0,
            userStats.total_admins || 0,
            userStats.total_sub_admins || 0,
            userStats.total_super_admins || 0,
          ],
          backgroundColor: [
            "#06b6d4", // Patients — Cyan
            "#f59e0b", // Doctors — Yellow
            "#ec4899", // Distributors — Pink
            "#6366f1", // Admins — Indigo
            "#10b981", // Sub Admins — Green
            "#ef4444", // Super Admins — Red
          ],
          borderWidth: 1,
          borderColor: "rgba(255, 255, 255, 0.1)",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#94a3b8",
            font: { family: "Outfit", size: 12 },
          },
        },
      },
    },
  });
}

// Generic Bar Chart creator — reusable for weekly order charts
function createWeeklyBarChart(canvasId, label, data, color) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  const chartVarName = canvasId + "Instance";
  if (window[chartVarName]) {
    window[chartVarName].destroy();
  }

  // Gradient fill
  let gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, color);
  gradient.addColorStop(1, "rgba(255, 255, 255, 0.05)");

  window[chartVarName] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: label,
          data: data.values,
          backgroundColor: gradient,
          borderColor: color,
          borderWidth: 1,
          borderRadius: 6,
          barPercentage: 0.6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0, color: "#94a3b8" },
          grid: { color: "rgba(255, 255, 255, 0.05)" },
        },
        x: {
          ticks: { color: "#94a3b8" },
          grid: { display: false },
        },
      },
    },
  });
}

// Render all 3 weekly order bar charts
function setupWeeklyCharts(weeklyStats) {
  if (!weeklyStats) return;
  createWeeklyBarChart(
    "weeklyDistributorChart",
    "Distributor Orders",
    { labels: weeklyStats.labels, values: weeklyStats.distributor },
    "#ec4899"
  );
  createWeeklyBarChart(
    "weeklyDoctorChart",
    "Doctor Orders",
    { labels: weeklyStats.labels, values: weeklyStats.doctor },
    "#f59e0b"
  );
  createWeeklyBarChart(
    "weeklyPatientChart",
    "Patient Orders",
    { labels: weeklyStats.labels, values: weeklyStats.patient },
    "#0ea5e9"
  );
}
