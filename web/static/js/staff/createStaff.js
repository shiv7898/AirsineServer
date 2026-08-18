// ============================================================================
// CREATE STAFF LOGIC
// ============================================================================

window.setupCreateStaffForm = function() {
    const form = document.getElementById('create-staff-form');
    if (!form) return;
    
    // Prevent multiple bindings
    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);
    
    newForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('admin_token');
        if (!token) {
            showToast('Session expired. Please login again.', 'error');
            setTimeout(() => { localStorage.clear(); if(window.showLoginPage) window.showLoginPage(); }, 1500);
            return;
        }

        // Collect permissions from checkboxes
        const permissionsObj = {
            dashboard: [],
            users: [],
            distributors: [],
            staff: [],
            products: [],
            orders: [],
            queries: []
        };
        if (document.getElementById('perm-dash-view') && document.getElementById('perm-dash-view').checked)     permissionsObj.dashboard.push('view');
        
        if (document.getElementById('perm-user-view') && document.getElementById('perm-user-view').checked)     permissionsObj.users.push('view');
        if (document.getElementById('perm-user-create') && document.getElementById('perm-user-create').checked) permissionsObj.users.push('create');
        if (document.getElementById('perm-user-edit') && document.getElementById('perm-user-edit').checked)     permissionsObj.users.push('edit');
        if (document.getElementById('perm-user-delete') && document.getElementById('perm-user-delete').checked) permissionsObj.users.push('delete');
        
        if (document.getElementById('perm-distributor-view') && document.getElementById('perm-distributor-view').checked)     permissionsObj.distributors.push('view');
        if (document.getElementById('perm-distributor-create') && document.getElementById('perm-distributor-create').checked) permissionsObj.distributors.push('create');
        if (document.getElementById('perm-distributor-edit') && document.getElementById('perm-distributor-edit').checked)     permissionsObj.distributors.push('edit');
        if (document.getElementById('perm-distributor-delete') && document.getElementById('perm-distributor-delete').checked) permissionsObj.distributors.push('delete');
        
        if (document.getElementById('perm-staff-view') && document.getElementById('perm-staff-view').checked)    permissionsObj.staff.push('view');
        if (document.getElementById('perm-staff-create') && document.getElementById('perm-staff-create').checked) permissionsObj.staff.push('create');
        if (document.getElementById('perm-staff-edit') && document.getElementById('perm-staff-edit').checked)     permissionsObj.staff.push('edit');
        if (document.getElementById('perm-staff-delete') && document.getElementById('perm-staff-delete').checked) permissionsObj.staff.push('delete');
        
        if (document.getElementById('perm-product-view') && document.getElementById('perm-product-view').checked)  permissionsObj.products.push('view');
        if (document.getElementById('perm-product-create') && document.getElementById('perm-product-create').checked) permissionsObj.products.push('create');
        if (document.getElementById('perm-product-edit') && document.getElementById('perm-product-edit').checked)  permissionsObj.products.push('edit');
        if (document.getElementById('perm-product-delete') && document.getElementById('perm-product-delete').checked)permissionsObj.products.push('delete');
        
        if (document.getElementById('perm-order-view') && document.getElementById('perm-order-view').checked)    permissionsObj.orders.push('view');
        if (document.getElementById('perm-order-edit') && document.getElementById('perm-order-edit').checked)    permissionsObj.orders.push('edit');
        
        if (document.getElementById('perm-query-view') && document.getElementById('perm-query-view').checked)    permissionsObj.queries.push('view');
        if (document.getElementById('perm-query-edit') && document.getElementById('perm-query-edit').checked)    permissionsObj.queries.push('edit');

        const staffPayload = {
            name: document.getElementById('staff-name') ? document.getElementById('staff-name').value : '',
            email: document.getElementById('staff-email') ? document.getElementById('staff-email').value : '',
            password: document.getElementById('staff-password') ? document.getElementById('staff-password').value : '',
            role: document.getElementById('staff-role') ? document.getElementById('staff-role').value : '',
            phone: document.getElementById('staff-phone') ? document.getElementById('staff-phone').value : '',
            gender: document.getElementById('staff-gender') ? document.getElementById('staff-gender').value : '',
            age: document.getElementById('staff-age') ? document.getElementById('staff-age').value : '0',
            dob: document.getElementById('staff-dob') ? document.getElementById('staff-dob').value : '',
            homeAddress: document.getElementById('staff-address') ? document.getElementById('staff-address').value : '',
            area: document.getElementById('staff-area') ? document.getElementById('staff-area').value : '',
            district: document.getElementById('staff-district') ? document.getElementById('staff-district').value : '',
            state: document.getElementById('staff-state') ? document.getElementById('staff-state').value : '',
            pincode: document.getElementById('staff-pincode') ? document.getElementById('staff-pincode').value : '',
            permissions: JSON.stringify(permissionsObj)
        };

        toggleLoader(true);
        try {
            const response = await fetch(API_ENDPOINTS.CREATE_STAFF, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(staffPayload)
            });

            const data = await response.json();
            toggleLoader(false);

            if (!response.ok) {
                const errMsg = (data.error && data.error.message)
                    || (Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : data.detail)
                    || 'Failed to create staff member';
                throw new Error(errMsg);
            }

            showToast(`✅ Staff account for "${staffPayload.name}" successfully created!`);
            newForm.reset();
            if (window.switchTab) window.switchTab('admin-staff-view');
            if (typeof window.fetchUsers === 'function') window.fetchUsers();
        } catch (err) {
            toggleLoader(false);
            showToast(err.message, 'error');
        }
    });
};

// Initialize the form listener on DOM load
document.addEventListener('DOMContentLoaded', window.setupCreateStaffForm);
