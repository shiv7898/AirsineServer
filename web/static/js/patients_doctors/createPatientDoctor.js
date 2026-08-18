// ============================================================================
// CREATE PATIENT / DOCTOR LOGIC
// ============================================================================

window.openCreateUserForm = function() {
    if (window.switchTab) window.switchTab('create-user-view');
    window.updateCreateUserForm();
    window.updateRolePills();
};

window.closeCreateUserForm = function() {
    if (window.switchTab) window.switchTab('users-view');
    const form = document.getElementById('create-standard-user-form');
    if (form) form.reset();
    const docFields = document.getElementById('doctor-fields');
    if (docFields) docFields.style.display = 'none';
    const distFields = document.getElementById('distributor-fields');
    if (distFields) distFields.style.display = 'none';
    
    // Reset role pills
    const roleSelect = document.getElementById('c-role');
    if (roleSelect) roleSelect.value = 'patient';
    window.updateRolePills();
};

window.updateRolePills = function() {
    const roleSelect = document.getElementById('c-role');
    if (!roleSelect) return;
    const role = roleSelect.value;
    const configs = {
        patient:     { pill: 'pill-patient',     border: '#06b6d4', bg: 'rgba(6,182,212,0.08)',  color: '#0891b2' },
        doctor:      { pill: 'pill-doctor',      border: '#f59e0b', bg: 'rgba(245,158,11,0.08)', color: '#d97706' },
        distributor: { pill: 'pill-distributor', border: '#ec4899', bg: 'rgba(236,72,153,0.08)', color: '#db2777' }
    };
    ['patient', 'doctor', 'distributor'].forEach(r => {
        const el = document.getElementById('pill-' + r);
        if (!el) return;
        const isActive = r === role;
        const c = configs[r];
        el.style.border    = isActive ? `2px solid ${c.border}` : '2px solid #e2e8f0';
        el.style.background = isActive ? c.bg : '#f8fafc';
        const innerText = el.querySelector('div:last-child');
        if (innerText) innerText.style.color = isActive ? c.color : '#64748b';
    });
};

window.updateCreateUserForm = function() {
    const roleSelect = document.getElementById('c-role');
    if (!roleSelect) return;
    const role = roleSelect.value;
    const doctorFields = document.getElementById('doctor-fields');
    const distributorFields = document.getElementById('distributor-fields');
    if (doctorFields) doctorFields.style.display = (role === 'doctor') ? 'block' : 'none';
    if (distributorFields) distributorFields.style.display = (role === 'distributor') ? 'block' : 'none';
};

// Close modal when clicking backdrop (guard: element may not exist)
const _createUserModal = document.getElementById('create-user-modal');
if (_createUserModal) {
    _createUserModal.addEventListener('click', function(e) {
        if (e.target === this && typeof window.closeCreateUserForm === 'function') {
            window.closeCreateUserForm();
        }
    });
}

window.submitCreateUser = async function(e) {
    if (e) e.preventDefault();
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    const role = document.getElementById('c-role') ? document.getElementById('c-role').value : 'patient';
    const dobVal = document.getElementById('c-dob') ? document.getElementById('c-dob').value : '';

    const payload = {
        name:        document.getElementById('c-name') ? document.getElementById('c-name').value.trim() : '',
        email:       document.getElementById('c-email') ? document.getElementById('c-email').value.trim() : '',
        password:    document.getElementById('c-password') ? document.getElementById('c-password').value : '',
        phone:       document.getElementById('c-phone') ? document.getElementById('c-phone').value.trim() : '',
        role:        role,
        gender:      document.getElementById('c-gender') ? document.getElementById('c-gender').value : '',
        age:         parseInt(document.getElementById('c-age') ? document.getElementById('c-age').value : '0'),
        dob:         dobVal || '01-01-2000',
        homeAddress: document.getElementById('c-address') ? document.getElementById('c-address').value.trim() : 'N/A',
        area:        document.getElementById('c-area') ? document.getElementById('c-area').value.trim() : 'N/A',
        district:    document.getElementById('c-district') ? document.getElementById('c-district').value.trim() : 'N/A',
        state:       document.getElementById('c-state') ? document.getElementById('c-state').value.trim() : 'N/A',
        pincode:     document.getElementById('c-pincode') ? document.getElementById('c-pincode').value.trim() : '',
    };

    // Doctor-specific fields
    if (role === 'doctor') {
        payload.hospital       = document.getElementById('c-hospital') ? document.getElementById('c-hospital').value.trim() : null;
        payload.specialisation = document.getElementById('c-specialisation') ? document.getElementById('c-specialisation').value.trim() : null;
        payload.qualification  = document.getElementById('c-qualification') ? document.getElementById('c-qualification').value.trim() : null;
        payload.experience     = document.getElementById('c-experience') ? document.getElementById('c-experience').value : null;
    }

    // Distributor-specific fields (in case they use the standard modal for distributor)
    if (role === 'distributor') {
        payload.companyName      = document.getElementById('c-company') ? document.getElementById('c-company').value.trim() : null;
        payload.businessType     = document.getElementById('c-business-type') ? document.getElementById('c-business-type').value.trim() : null;
        payload.licenseNumber    = document.getElementById('c-license') ? document.getElementById('c-license').value.trim() : null;
    }

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
            const errMsg = (data.error && data.error.message) || data.detail || 'Failed to create user';
            throw new Error(errMsg);
        }

        showToast(`✅ User "${data.name}" created with ID: ${data.custom_id || data.id}`);
        if (window.switchTab) window.switchTab('users-view');
        if (typeof window.fetchUsers === 'function') window.fetchUsers();
        
        const form = document.getElementById('create-standard-user-form');
        if (form) form.reset();
    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
};
