// ============================================================================
// users_shared/userDetailUI.js
// Shared UI logic for the User Detail page (user-detail.html)
// Functions: setUdField, goBackFromDetail, enableDetailEdit,
//            cancelDetailEdit, saveUserEdit
// Used by: patients_doctors, distributors, staff view/edit files
// ============================================================================

// Global state for the user detail page
window.originalUserData = null;  // Cached user data for cancel/restore
window.detailBackTab = 'users-view';  // Which tab to return to on back

// Setters so role-specific view files can write to these globals
window.setOriginalUserData = (data) => { window.originalUserData = data; };
window.setDetailBackTab = (tab) => { window.detailBackTab = tab; };

// ─────────────────────────────────────────────────────────────
// setUdField(viewId, editId, value, isSelect)
// Populates both the read-only (.ud-value) and editable (.ud-input)
// elements for a single field in the user detail form.
// ─────────────────────────────────────────────────────────────
window.setUdField = function(viewId, editId, value, isSelect) {
    const vEl = document.getElementById(viewId);
    const eEl = document.getElementById(editId);
    const displayVal = (value !== null && value !== undefined && value !== '') ? value : null;
    if (vEl) { vEl.textContent = displayVal || 'N/A'; vEl.className = 'ud-value' + (displayVal ? '' : ' na'); }
    if (eEl) {
        if (isSelect) { [...eEl.options].forEach(o => o.selected = o.value === value || o.text === value); }
        else { eEl.value = displayVal || ''; }
    }
};

// ─────────────────────────────────────────────────────────────
// goBackFromDetail()
// Navigates back to the correct tab when user clicks "Back" button
// ─────────────────────────────────────────────────────────────
function goBackFromDetail() {
    switchTab(window.detailBackTab);
}

// ─────────────────────────────────────────────────────────────
// enableDetailEdit()
// Switches the user detail page into edit mode:
//   - Hides .ud-value spans, shows .ud-input fields
//   - Shows Save/Cancel buttons, hides Edit button
//   - Shows permissions edit checkboxes if super_admin editing admin
// ─────────────────────────────────────────────────────────────
window.enableDetailEdit = function() {
    document.querySelectorAll('#user-detail-view .ud-value').forEach(el => el.style.display = 'none');
    document.querySelectorAll('#user-detail-view .ud-input').forEach(el => el.style.display = 'block');

    const editBtn = document.getElementById('detail-edit-btn');
    if (editBtn) editBtn.style.display = 'none';
    document.getElementById('detail-save-btn').style.display = 'inline-flex';
    const cancelBtn = document.getElementById('detail-cancel-btn');
    if (cancelBtn) cancelBtn.style.display = 'inline-flex';

    const loggedInRole = localStorage.getItem('admin_role');
    const isSuperAdmin = loggedInRole === 'super_admin';
    const editedRole = window.originalUserData ? window.originalUserData.role : '';
    const isEditedAdmin = ['admin', 'sub_admin'].includes(editedRole);

    const permEditSection = document.getElementById('ud-permissions-edit-section');
    if (isSuperAdmin && isEditedAdmin) {
        const permSection = document.getElementById('ud-permissions-section');
        if (permSection) permSection.style.display = 'none';
        if (permEditSection) permEditSection.style.display = 'block';
    } else {
        if (permEditSection) permEditSection.style.display = 'none';
    }
};

// ─────────────────────────────────────────────────────────────
// closeEditUser()
// Reverts edit mode: restores cached values, hides inputs,
// shows read-only values and Edit button again
// ─────────────────────────────────────────────────────────────
window.closeEditUser = function() {
    if (window.originalUserData) {
        const user = window.originalUserData;
        window.setUdField('v-name', 'e-name', user.name);
        window.setUdField('v-phone', 'e-phone', user.phone);
        window.setUdField('v-email', 'e-email', user.email);
        window.setUdField('v-gender', 'e-gender', user.gender, true);
        window.setUdField('v-dob', 'e-dob', user.dob);
        window.setUdField('v-age', 'e-age', user.age);
        window.setUdField('v-role', 'e-role', user.role);
        window.setUdField('v-status', 'e-status', user.status || 'Active', true);
        window.setUdField('v-verification', 'e-verification', user.verificationStatus || 'Pending', true);
        window.setUdField('v-commission', 'e-commission', user.commission);
        window.setUdField('v-discount-field', 'e-discount', user.discount);
        window.setUdField('v-address', 'e-address', user.homeAddress);
        window.setUdField('v-area', 'e-area', user.area);
        window.setUdField('v-state', 'e-state', user.state);
        window.setUdField('v-district', 'e-district', user.district);
        window.setUdField('v-pincode', 'e-pincode', user.pincode);

        // Role-specific fields restore
        const eHosp = document.getElementById('e-hospital'); if(eHosp) eHosp.value = user.hospital || '';
        const eSpec = document.getElementById('e-specialisation'); if(eSpec) eSpec.value = user.specialisation || '';
        const eQual = document.getElementById('e-qualification'); if(eQual) eQual.value = user.qualification || '';
        const eExp = document.getElementById('e-experience'); if(eExp) eExp.value = user.experience || '';
        const eComp = document.getElementById('e-companyName'); if(eComp) eComp.value = user.companyName || '';
        const eBus = document.getElementById('e-businessType'); if(eBus) eBus.value = user.businessType || '';
        const eDist = document.getElementById('e-distributorType'); if(eDist) eDist.value = user.distributorType || '';
        const eLic = document.getElementById('e-licenseNumber'); if(eLic) eLic.value = user.licenseNumber || '';
    }

    document.querySelectorAll('#user-detail-view .ud-value').forEach(el => el.style.display = 'flex');
    document.querySelectorAll('#user-detail-view .ud-input').forEach(el => el.style.display = 'none');

    const editBtn = document.getElementById('detail-edit-btn');
    if (editBtn) editBtn.style.display = 'inline-flex';
    document.getElementById('detail-save-btn').style.display = 'none';
    const cancelBtn = document.getElementById('detail-cancel-btn');
    if (cancelBtn) cancelBtn.style.display = 'none';

    const permEditSection = document.getElementById('ud-permissions-edit-section');
    if (permEditSection) permEditSection.style.display = 'none';

    const editedRole = window.originalUserData ? window.originalUserData.role : '';
    const isEditedAdmin = ['admin', 'sub_admin'].includes(editedRole);
    const permSection = document.getElementById('ud-permissions-section');
    if (isEditedAdmin && permSection) permSection.style.display = 'block';
};

// ─────────────────────────────────────────────────────────────
// saveUserEdit()
// Collects all form values, builds payload, sends PUT to API
// Called from user-detail.html Save button
// ─────────────────────────────────────────────────────────────
async function saveUserEdit() {
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    const userId = document.getElementById('ud-current-user-id').value;
    if (!userId) return;

    const payload = {
        name: document.getElementById('e-name').value.trim(),
        email: document.getElementById('e-email').value.trim(),
        phone: document.getElementById('e-phone').value.trim(),
        gender: document.getElementById('e-gender').value,
        dob: document.getElementById('e-dob').value,
        age: parseInt(document.getElementById('e-age').value) || null,
        status: document.getElementById('e-status').value,
        verification_status: document.getElementById('e-verification').value,
        commission: parseFloat(document.getElementById('e-commission').value) || 0.0,
        discount: parseFloat(document.getElementById('e-discount').value) || 0.0,
        homeAddress: document.getElementById('e-address').value.trim(),
        area: document.getElementById('e-area').value.trim(),
        district: document.getElementById('e-district').value.trim(),
        state: document.getElementById('e-state').value.trim(),
        pincode: document.getElementById('e-pincode').value.trim()
    };

    // Add permissions if super_admin editing admin/sub_admin
    const isSuperAdmin = localStorage.getItem('admin_role') === 'super_admin';
    const editedRole = window.originalUserData ? window.originalUserData.role : '';
    if (isSuperAdmin && ['admin', 'sub_admin'].includes(editedRole)) {
        payload.permissions = buildPermissionsPayload();
    }

    // Role-specific fields (Doctor / Distributor)
    const eHosp = document.getElementById('e-hospital'); if(eHosp) payload.hospital = eHosp.value.trim();
    const eSpec = document.getElementById('e-specialisation'); if(eSpec) payload.specialisation = eSpec.value.trim();
    const eQual = document.getElementById('e-qualification'); if(eQual) payload.qualification = eQual.value.trim();
    const eExp = document.getElementById('e-experience'); if(eExp) payload.experience = parseInt(eExp.value) || null;
    const eComp = document.getElementById('e-companyName'); if(eComp) payload.companyName = eComp.value.trim();
    const eBus = document.getElementById('e-businessType'); if(eBus) payload.businessType = eBus.value.trim();
    const eDist = document.getElementById('e-distributorType'); if(eDist) payload.distributorType = eDist.value.trim();
    const eLic = document.getElementById('e-licenseNumber'); if(eLic) payload.licenseNumber = eLic.value.trim();

    toggleLoader(true);
    try {
        const url = API_ENDPOINTS.EDIT_USER_DATA(userId, editedRole);
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        toggleLoader(false);
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to save edits');

        showToast('✅ User updated successfully!', 'success');
        // Reload via router so the correct view function is called
        viewUser(userId, false, editedRole);
    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
}
