// ============================================================================
// EDIT DISTRIBUTOR LOGIC
// ============================================================================

window.editDistributor = function(userId) {
    const editBtn = document.getElementById('detail-edit-btn');
    const saveBtn = document.getElementById('detail-save-btn');
    const cancelBtn = document.getElementById('detail-cancel-btn');
    
    if (editBtn) editBtn.style.display = 'none';
    if (saveBtn) saveBtn.style.display = 'block';
    if (cancelBtn) cancelBtn.style.display = 'block';

    // Show inputs, hide values
    document.querySelectorAll('.ud-value').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.ud-input').forEach(el => el.style.display = 'block');

    // Permissions (Hide for distributor)
    const permSection = document.getElementById('ud-permissions-section');
    if (permSection) permSection.style.display = 'none';
};

window.submitUpdateDistributorRole = async function() {
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

    // Distributor specific fields
    payload.companyName = document.getElementById('e-companyName') ? document.getElementById('e-companyName').value : null;
    payload.businessType = document.getElementById('e-businessType') ? document.getElementById('e-businessType').value : null;
    payload.distributorType = document.getElementById('e-distributorType') ? document.getElementById('e-distributorType').value : null;
    payload.licenseNumber = document.getElementById('e-licenseNumber') ? document.getElementById('e-licenseNumber').value : null;

    toggleLoader(true);
    try {
        const url = API_ENDPOINTS.UPDATE_USER(userId, 'distributor');
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

        if (!response.ok) throw new Error(data.detail || 'Failed to update distributor');

        showToast('Distributor updated successfully!');
        if (typeof window.closeEditUser === 'function') window.closeEditUser();
        
        // Refresh details and table
        if (typeof window.viewDistributor === 'function') window.viewDistributor(userId, false);
        if (typeof window.fetchUsers === 'function') window.fetchUsers();
    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
};
