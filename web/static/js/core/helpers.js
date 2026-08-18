// ============================================================================
// core/helpers.js — Common Utility Functions
// Reusable helpers used across multiple modules
// ============================================================================

// Calculate Age from Date of Birth and fill into input field
function calculateAgeFromDOB(dobStr, targetInputId) {
  if (!dobStr) return;
  const today = new Date();
  const dob = new Date(dobStr);
  let age = today.getFullYear() - dob.getFullYear();
  if (
    today.getMonth() < dob.getMonth() ||
    (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate())
  ) {
    age--;
  }
  const target = document.getElementById(targetInputId);
  if (target) {
    target.value = age;
  }
}

// Filter Table Rows — live search/filter on any table
function filterTable(tbodyId, query) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  const rows = tbody.querySelectorAll("tr");
  const lowerQuery = query.toLowerCase().trim();
  rows.forEach((row) => {
    const text = row.innerText.toLowerCase();
    row.style.display = text.includes(lowerQuery) ? "" : "none";
  });
}
