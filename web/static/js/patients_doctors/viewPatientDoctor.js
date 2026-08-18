// ============================================================================
// VIEW PATIENT / DOCTOR LOGIC
// ============================================================================

window.viewPatientDoctor = async function(userId, editMode = false, role = null) {
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    if (!role) {
        if (window.location.pathname.startsWith('/user-view/') || window.location.pathname.startsWith('/user-edit/')) {
            role = 'patient';
        }
    }

    toggleLoader(true);
    try {
        const url = API_ENDPOINTS.USER_DETAIL(userId, role);
        const response = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
        toggleLoader(false);
        if (!response.ok) throw new Error(`Failed to fetch ${role} data`);
        const user = await response.json();
        
        if (typeof window.setOriginalUserData === 'function') window.setOriginalUserData(user);
        if (typeof window.setDetailBackTab === 'function') window.setDetailBackTab('users-view');

        // 1. Populate top identity and quick stats
        const initials = (user.name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        document.getElementById('ud-avatar').textContent = initials;
        document.getElementById('ud-name').textContent = user.name || 'N/A';
        
        // Badges
        const roleBadge = document.getElementById('ud-role-badge');
        roleBadge.className = `ud-badge ${user.role}`;
        roleBadge.innerHTML = `<i class="fa-solid fa-user-tag"></i> ${(user.role || 'N/A').replace(/_/g, ' ').toUpperCase()}`;
        
        const statusBadge = document.getElementById('ud-status-badge');
        statusBadge.className = `ud-badge ${user.status || 'Active'}`;
        statusBadge.innerHTML = `<i class="fa-solid fa-circle-info"></i> ${user.status || 'Active'}`;
        
        const verifyBadge = document.getElementById('ud-verify-badge');
        verifyBadge.className = `ud-badge ${user.verificationStatus || 'Pending'}`;
        verifyBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${user.verificationStatus || 'Pending'}`;
        
        // Details Grid
        document.getElementById('ud-current-user-id').value = user.id;
        document.getElementById('ud-id').textContent = user.customId || user.id;
        document.getElementById('ud-created').textContent = user.createdAt ? new Date(user.createdAt).toLocaleDateString('en-IN') : 'N/A';
        document.getElementById('ud-orders').textContent = user.totalOrders || 0;
        document.getElementById('ud-commission').textContent = user.commission !== undefined ? `${user.commission}%` : '0%';
        document.getElementById('ud-discount').textContent = user.discount !== undefined ? `${user.discount}%` : '0%';
        document.getElementById('ud-referral').textContent = user.referralCode || 'N/A';
        document.getElementById('ud-last-login').textContent = user.lastLogin ? new Date(user.lastLogin).toLocaleString('en-IN') : 'Never';

        // 2. Populate basic and address info view & edit values
        if (typeof window.setUdField === 'function') {
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
        }

        // 3. Dynamic role-specific fields for Doctor
        const roleSection = document.getElementById('ud-role-section');
        const roleTitle = document.getElementById('ud-role-section-title');
        const roleFields = document.getElementById('ud-role-fields');

        if (user.role === 'doctor') {
            if (roleSection) roleSection.style.display = 'block';
            if (roleTitle) roleTitle.innerHTML = '<i class="fa-solid fa-stethoscope" style="color: var(--accent-primary);"></i> Doctor Professional Details';
            if (roleFields) {
                roleFields.innerHTML = `
                    <div class="ud-field">
                        <div class="ud-label">Hospital</div>
                        <div class="ud-value" id="v-hospital">${user.hospital || 'N/A'}</div>
                        <input class="ud-input" id="e-hospital" type="text" style="display:none;" value="${user.hospital || ''}">
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Specialisation</div>
                        <div class="ud-value" id="v-specialisation">${user.specialisation || 'N/A'}</div>
                        <input class="ud-input" id="e-specialisation" type="text" style="display:none;" value="${user.specialisation || ''}">
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Qualification</div>
                        <div class="ud-value" id="v-qualification">${user.qualification || 'N/A'}</div>
                        <input class="ud-input" id="e-qualification" type="text" style="display:none;" value="${user.qualification || ''}">
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Experience (Years)</div>
                        <div class="ud-value" id="v-experience">${user.experience || 'N/A'}</div>
                        <input class="ud-input" id="e-experience" type="number" style="display:none;" value="${user.experience || ''}">
                    </div>
                `;
            }
        } else {
            if (roleSection) roleSection.style.display = 'none';
            if (roleFields) roleFields.innerHTML = '';
        }

        // 4. Permissions section (Hide for patients/doctors)
        const permSection = document.getElementById('ud-permissions-section');
        if (permSection) permSection.style.display = 'none';

        // 5. Populate Documents
        const docsGrid = document.getElementById('ud-docs-grid');
        if (docsGrid) {
            docsGrid.innerHTML = '';
            const docs = user.documents || [];
            if (docs.length === 0) {
                docsGrid.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; font-style: italic;">No documents uploaded.</div>';
            } else {
                docs.forEach(doc => {
                    docsGrid.innerHTML += `
                        <div class="ud-doc-card">
                            <i class="fa-solid fa-file-pdf"></i>
                            <div style="flex: 1; min-width: 0;">
                                <div style="font-weight: 600; color: var(--text-primary); font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${doc.docName}</div>
                                <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${doc.docType || 'Document'}</div>
                            </div>
                            <div style="display: flex; gap: 8px;">
                                <a href="${doc.docUrl}" target="_blank" style="color: var(--accent-primary); cursor: pointer;"><i class="fa-solid fa-eye"></i></a>
                                <a href="${doc.docUrl}" download style="color: var(--text-muted); cursor: pointer;"><i class="fa-solid fa-download"></i></a>
                            </div>
                        </div>
                    `;
                });
            }
        }

        // 6. Handle Switch to detail view
        if (window.switchTab) window.switchTab('user-detail-view');

        if (editMode && typeof window.editPatientDoctor === 'function') {
            window.editPatientDoctor(userId, user.role);
        } else if (typeof window.closeEditUser === 'function') {
            window.closeEditUser(); 
        }

    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
};
