// ============================================================================
// EDIT STAFF LOGIC
// ============================================================================

window.editStaff = function(userId, role) {
    const editBtn = document.getElementById('detail-edit-btn');
    const saveBtn = document.getElementById('detail-save-btn');
    const cancelBtn = document.getElementById('detail-cancel-btn');
    
    if (editBtn) editBtn.style.display = 'none';
    if (saveBtn) saveBtn.style.display = 'block';
    if (cancelBtn) cancelBtn.style.display = 'block';

    // Show inputs, hide values
    document.querySelectorAll('.ud-value').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.ud-input').forEach(el => el.style.display = 'block');

    // Permissions (Show for staff)
    const permSection = document.getElementById('ud-permissions-section');
    if (permSection) {
        permSection.style.display = 'block';
        const permList = document.getElementById('ud-permissions-list');
        const permEdit = document.getElementById('ud-permissions-edit');
        if (permList) permList.style.display = 'none';
        if (permEdit) permEdit.style.display = 'block';
    }
};

window.submitUpdateStaffRole = async function() {
    const userId = document.getElementById('ud-current-user-id').value;
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    // Collect base payload
    const payload = {
        name: document.getElementById('e-name').value,
        phone: document.getElementById('e-phone').value,
        email: document.getElementById('e-email').value,
        gender: document.getElementById('e-gender').value,
        dob: document.getElementById('e-dob').value,
        age: parseInt(document.getElementById('e-age').value) || null,
        status: document.getElementById('e-status').value,
        verificationStatus: document.getElementById('e-verification').value,
        commission: parseFloat(document.getElementById('e-commission').value) || 0,
        discount: parseFloat(document.getElementById('e-discount').value) || 0,

        homeAddress: document.getElementById('e-address').value,
        area: document.getElementById('e-area').value,
        state: document.getElementById('e-state').value,
        district: document.getElementById('e-district').value,
        pincode: document.getElementById('e-pincode').value
    };

    const role = window.originalUserData ? window.originalUserData.role : 'admin';

    // Collect Permissions
    const permissionsObj = {
        users: [],
        distributors: [],
        staff: [],
        products: [],
        orders: [],
        queries: []
    };
    if (document.getElementById('ep-perm-user-view') && document.getElementById('ep-perm-user-view').checked)     permissionsObj.users.push('view');
    if (document.getElementById('ep-perm-user-create') && document.getElementById('ep-perm-user-create').checked) permissionsObj.users.push('create');
    if (document.getElementById('ep-perm-user-edit') && document.getElementById('ep-perm-user-edit').checked)     permissionsObj.users.push('edit');
    if (document.getElementById('ep-perm-user-delete') && document.getElementById('ep-perm-user-delete').checked) permissionsObj.users.push('delete');

    if (document.getElementById('ep-perm-distributor-view') && document.getElementById('ep-perm-distributor-view').checked)     permissionsObj.distributors.push('view');
    if (document.getElementById('ep-perm-distributor-create') && document.getElementById('ep-perm-distributor-create').checked) permissionsObj.distributors.push('create');
    if (document.getElementById('ep-perm-distributor-edit') && document.getElementById('ep-perm-distributor-edit').checked)     permissionsObj.distributors.push('edit');
    if (document.getElementById('ep-perm-distributor-delete') && document.getElementById('ep-perm-distributor-delete').checked) permissionsObj.distributors.push('delete');

    if (document.getElementById('ep-perm-staff-view') && document.getElementById('ep-perm-staff-view').checked)    permissionsObj.staff.push('view');
    if (document.getElementById('ep-perm-staff-create') && document.getElementById('ep-perm-staff-create').checked) permissionsObj.staff.push('create');
    if (document.getElementById('ep-perm-staff-edit') && document.getElementById('ep-perm-staff-edit').checked)     permissionsObj.staff.push('edit');
    if (document.getElementById('ep-perm-staff-delete') && document.getElementById('ep-perm-staff-delete').checked) permissionsObj.staff.push('delete');

    if (document.getElementById('ep-perm-product-view') && document.getElementById('ep-perm-product-view').checked)  permissionsObj.products.push('view');
    if (document.getElementById('ep-perm-product-create') && document.getElementById('ep-perm-product-create').checked) permissionsObj.products.push('create');
    if (document.getElementById('ep-perm-product-edit') && document.getElementById('ep-perm-product-edit').checked)  permissionsObj.products.push('edit');
    if (document.getElementById('ep-perm-product-delete') && document.getElementById('ep-perm-product-delete').checked)permissionsObj.products.push('delete');

    if (document.getElementById('ep-perm-order-view') && document.getElementById('ep-perm-order-view').checked)    permissionsObj.orders.push('view');
    if (document.getElementById('ep-perm-order-edit') && document.getElementById('ep-perm-order-edit').checked)    permissionsObj.orders.push('edit');

    if (document.getElementById('ep-perm-query-view') && document.getElementById('ep-perm-query-view').checked)    permissionsObj.queries.push('view');
    if (document.getElementById('ep-perm-query-edit') && document.getElementById('ep-perm-query-edit').checked)    permissionsObj.queries.push('edit');

    payload.permissions = JSON.stringify(permissionsObj);

    toggleLoader(true);
    try {
        const url = API_ENDPOINTS.UPDATE_USER(userId, role);
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        toggleLoader(false);

        if (!response.ok) throw new Error(data.detail || `Failed to update ${role}`);

        showToast(`${role.replace('_', ' ').toUpperCase()} updated successfully!`);
        
        // Hide edit list, show view list again
        const permList = document.getElementById('ud-permissions-list');
        const permEdit = document.getElementById('ud-permissions-edit');
        if (permList) permList.style.display = 'flex';
        if (permEdit) permEdit.style.display = 'none';
        
        if (typeof window.closeEditUser === 'function') window.closeEditUser();
        
        // Refresh details and table
        if (typeof window.viewStaff === 'function') window.viewStaff(userId, false, role);
        if (typeof window.fetchUsers === 'function') window.fetchUsers();
    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
};

window.closeEditUserOverrides = function() {
    const permList = document.getElementById('ud-permissions-list');
    const permEdit = document.getElementById('ud-permissions-edit');
    if (permList) permList.style.display = 'flex';
    if (permEdit) permEdit.style.display = 'none';
    if (typeof window.closeEditUser === 'function') window.closeEditUser();
};
// Attach this to the cancel button dynamically or in html
const cancelBtn = document.getElementById('ud-cancel-btn');
if(cancelBtn) {
    cancelBtn.onclick = window.closeEditUserOverrides;
}
