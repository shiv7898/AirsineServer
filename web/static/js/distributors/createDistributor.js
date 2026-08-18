// ============================================================================
// CREATE DISTRIBUTOR LOGIC
// ============================================================================

window.submitCreateDistributor = async function(e) {
    if (e) e.preventDefault();
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    const role = 'distributor';
    const dobVal = document.getElementById('d-dob') ? document.getElementById('d-dob').value : '';

    const payload = {
        name:        document.getElementById('d-name') ? document.getElementById('d-name').value.trim() : '',
        email:       document.getElementById('d-email') ? document.getElementById('d-email').value.trim() : '',
        password:    document.getElementById('d-password') ? document.getElementById('d-password').value : '',
        phone:       document.getElementById('d-phone') ? document.getElementById('d-phone').value.trim() : '',
        role:        role,
        gender:      document.getElementById('d-gender') ? document.getElementById('d-gender').value : '',
        age:         parseInt(document.getElementById('d-age') ? document.getElementById('d-age').value : '0'),
        dob:         dobVal || '01-01-2000',
        homeAddress: document.getElementById('d-address') ? document.getElementById('d-address').value.trim() : 'N/A',
        area:        document.getElementById('d-area') ? document.getElementById('d-area').value.trim() : 'N/A',
        district:    document.getElementById('d-district') ? document.getElementById('d-district').value.trim() : 'N/A',
        state:       document.getElementById('d-state') ? document.getElementById('d-state').value.trim() : 'N/A',
        pincode:     document.getElementById('d-pincode') ? document.getElementById('d-pincode').value.trim() : '',
        companyName: document.getElementById('d-company') ? document.getElementById('d-company').value.trim() : null,
        businessType:document.getElementById('d-business-type') ? document.getElementById('d-business-type').value.trim() : null,
        licenseNumber:document.getElementById('d-license') ? document.getElementById('d-license').value.trim() : null,
    };

    toggleLoader(true);
    try {
        const response = await fetch(API_ENDPOINTS.USERS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        toggleLoader(false);

        if (!response.ok) {
            const errMsg = (data.error && data.error.message) || data.detail || 'Failed to create distributor';
            throw new Error(errMsg);
        }

        showToast(`✅ Distributor "${data.name}" created with ID: ${data.custom_id || data.id}`);
        if (window.switchTab) window.switchTab('distributors-view');
        if (typeof window.fetchUsers === 'function') window.fetchUsers();
        
        const form = document.getElementById('create-distributor-form');
        if (form) form.reset();
    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
};
