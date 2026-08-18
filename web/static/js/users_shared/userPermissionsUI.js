// ============================================================================
// users_shared/userPermissionsUI.js
// Handles the permissions UI in the User Detail page:
//   - Rendering the permissions display section (badges)
//   - Populating edit checkboxes from user's permissions
//   - Building the permissions payload from checkboxes on save
// ============================================================================

// All permission checkbox IDs used in the edit form
const PERM_CHECKBOX_IDS = [
    'ep-perm-user-view', 'ep-perm-user-create', 'ep-perm-user-edit', 'ep-perm-user-delete',
    'ep-perm-distributor-view', 'ep-perm-distributor-create', 'ep-perm-distributor-edit', 'ep-perm-distributor-delete',
    'ep-perm-staff-view', 'ep-perm-staff-create', 'ep-perm-staff-edit', 'ep-perm-staff-delete',
    'ep-perm-product-view', 'ep-perm-product-create', 'ep-perm-product-edit', 'ep-perm-product-delete',
    'ep-perm-order-view', 'ep-perm-order-edit',
    'ep-perm-query-view', 'ep-perm-query-edit'
];

// ─────────────────────────────────────────────────────────────
// resetPermissionCheckboxes()
// Unchecks all permission checkboxes in the edit form
// ─────────────────────────────────────────────────────────────
function resetPermissionCheckboxes() {
    PERM_CHECKBOX_IDS.forEach(id => {
        const cb = document.getElementById(id);
        if (cb) cb.checked = false;
    });
}

// ─────────────────────────────────────────────────────────────
// renderPermissionsSection(user)
// Shows/hides the permissions panel and renders permission badges.
// Also populates the edit checkboxes from the user's stored permissions.
// Only shown for admin / sub_admin roles.
// ─────────────────────────────────────────────────────────────
function renderPermissionsSection(user) {
    resetPermissionCheckboxes();

    const permSection = document.getElementById('ud-permissions-section');
    const permList = document.getElementById('ud-permissions-list');

    if ((user.role === 'admin' || user.role === 'sub_admin') && user.permissions) {
        permSection.style.display = 'block';
        let permHtml = '';

        try {
            const p = JSON.parse(user.permissions);

            // Build badge HTML for each module
            for (const [module, actions] of Object.entries(p)) {
                if (actions.length > 0) {
                    permHtml += `
                        <div style="background: rgba(248, 250, 252, 0.8); border: 1px solid var(--border-glass); border-radius: 12px; padding: 12px 16px; min-width: 150px;">
                            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 8px; letter-spacing: 0.5px;">${module}</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                    `;
                    actions.forEach(act => {
                        permHtml += `<span style="background: rgba(14, 165, 233, 0.1); color: #0284c7; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; text-transform: uppercase;">${act}</span>`;
                    });
                    permHtml += `</div></div>`;
                }
            }

            if (!permHtml) {
                permHtml = '<span style="color: var(--text-muted); font-style: italic;">No permissions assigned.</span>';
            }

            // Populate edit checkboxes from stored permissions
            const check = (id) => { const el = document.getElementById(id); if (el) el.checked = true; };

            if (p.users) {
                if (p.users.includes('view'))   check('ep-perm-user-view');
                if (p.users.includes('create')) check('ep-perm-user-create');
                if (p.users.includes('edit'))   check('ep-perm-user-edit');
                if (p.users.includes('delete')) check('ep-perm-user-delete');
            }
            if (p.distributors) {
                if (p.distributors.includes('view'))   check('ep-perm-distributor-view');
                if (p.distributors.includes('create')) check('ep-perm-distributor-create');
                if (p.distributors.includes('edit'))   check('ep-perm-distributor-edit');
                if (p.distributors.includes('delete')) check('ep-perm-distributor-delete');
            }
            if (p.staff) {
                if (p.staff.includes('view'))   check('ep-perm-staff-view');
                if (p.staff.includes('create')) check('ep-perm-staff-create');
                if (p.staff.includes('edit'))   check('ep-perm-staff-edit');
                if (p.staff.includes('delete')) check('ep-perm-staff-delete');
            }
            if (p.products) {
                if (p.products.includes('view'))   check('ep-perm-product-view');
                if (p.products.includes('create')) check('ep-perm-product-create');
                if (p.products.includes('edit'))   check('ep-perm-product-edit');
                if (p.products.includes('delete')) check('ep-perm-product-delete');
            }
            if (p.orders) {
                if (p.orders.includes('view')) check('ep-perm-order-view');
                if (p.orders.includes('edit')) check('ep-perm-order-edit');
            }
            if (p.queries) {
                if (p.queries.includes('view')) check('ep-perm-query-view');
                if (p.queries.includes('edit')) check('ep-perm-query-edit');
            }

        } catch (e) {
            permHtml = '<span style="color: var(--text-muted); font-style: italic;">Error parsing permissions.</span>';
        }

        permList.innerHTML = permHtml;

    } else {
        permSection.style.display = 'none';
        permList.innerHTML = '';
    }
}

// ─────────────────────────────────────────────────────────────
// buildPermissionsPayload()
// Reads all permission checkboxes and returns a JSON string
// representing the permissions object to send in the API payload.
// Called during saveUserEdit() when editing an admin/sub_admin.
// ─────────────────────────────────────────────────────────────
function buildPermissionsPayload() {
    const perms = {
        dashboard: ['view'], // dashboard view is always allowed
        users: [],
        distributors: [],
        staff: [],
        products: [],
        orders: [],
        queries: []
    };

    const isChecked = (id) => { const el = document.getElementById(id); return el && el.checked; };

    if (isChecked('ep-perm-user-view'))   perms.users.push('view');
    if (isChecked('ep-perm-user-create')) perms.users.push('create');
    if (isChecked('ep-perm-user-edit'))   perms.users.push('edit');
    if (isChecked('ep-perm-user-delete')) perms.users.push('delete');

    if (isChecked('ep-perm-distributor-view'))   perms.distributors.push('view');
    if (isChecked('ep-perm-distributor-create')) perms.distributors.push('create');
    if (isChecked('ep-perm-distributor-edit'))   perms.distributors.push('edit');
    if (isChecked('ep-perm-distributor-delete')) perms.distributors.push('delete');

    if (isChecked('ep-perm-staff-view'))   perms.staff.push('view');
    if (isChecked('ep-perm-staff-create')) perms.staff.push('create');
    if (isChecked('ep-perm-staff-edit'))   perms.staff.push('edit');
    if (isChecked('ep-perm-staff-delete')) perms.staff.push('delete');

    if (isChecked('ep-perm-product-view'))   perms.products.push('view');
    if (isChecked('ep-perm-product-create')) perms.products.push('create');
    if (isChecked('ep-perm-product-edit'))   perms.products.push('edit');
    if (isChecked('ep-perm-product-delete')) perms.products.push('delete');

    if (isChecked('ep-perm-order-view')) perms.orders.push('view');
    if (isChecked('ep-perm-order-edit')) perms.orders.push('edit');

    if (isChecked('ep-perm-query-view')) perms.queries.push('view');
    if (isChecked('ep-perm-query-edit')) perms.queries.push('edit');

    return JSON.stringify(perms);
}
