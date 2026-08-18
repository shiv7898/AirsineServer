// ============================================================================
// VIEW STAFF LOGIC
// ============================================================================

window.viewStaff = async function(userId, editMode = false, role = null) {
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    if (!role) {
        if (window.location.pathname.startsWith('/staff-view/') || window.location.pathname.startsWith('/staff-edit/')) {
            role = 'admin';
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
        if (typeof window.setDetailBackTab === 'function') window.setDetailBackTab('admin-staff-view');

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

        // 3. Dynamic role-specific fields (Hide for staff)
        const roleSection = document.getElementById('ud-role-section');
        const roleFields = document.getElementById('ud-role-fields');
        if (roleSection) roleSection.style.display = 'none';
        if (roleFields) roleFields.innerHTML = '';

        // 4. Permissions section
        // Reset edit permissions checkboxes
        const permCheckboxes = [
            'ep-perm-user-view', 'ep-perm-user-create', 'ep-perm-user-edit', 'ep-perm-user-delete',
            'ep-perm-distributor-view', 'ep-perm-distributor-create', 'ep-perm-distributor-edit', 'ep-perm-distributor-delete',
            'ep-perm-staff-view', 'ep-perm-staff-create', 'ep-perm-staff-edit', 'ep-perm-staff-delete',
            'ep-perm-product-view', 'ep-perm-product-create', 'ep-perm-product-edit', 'ep-perm-product-delete',
            'ep-perm-order-view', 'ep-perm-order-edit',
            'ep-perm-query-view', 'ep-perm-query-edit'
        ];
        permCheckboxes.forEach(id => {
            const cb = document.getElementById(id);
            if (cb) cb.checked = false;
        });

        const permSection = document.getElementById('ud-permissions-section');
        const permList = document.getElementById('ud-permissions-list');
        
        if (user.permissions) {
            if (permSection) permSection.style.display = 'block';
            let permHtml = '';
            try {
                const p = JSON.parse(user.permissions);
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
                if (!permHtml) permHtml = '<span style="color: var(--text-muted); font-style: italic;">No permissions assigned.</span>';

                // Populate edit checkboxes
                if (p.users) {
                    if (p.users.includes('view')) document.getElementById('ep-perm-user-view').checked = true;
                    if (p.users.includes('create')) document.getElementById('ep-perm-user-create').checked = true;
                    if (p.users.includes('edit')) document.getElementById('ep-perm-user-edit').checked = true;
                    if (p.users.includes('delete')) document.getElementById('ep-perm-user-delete').checked = true;
                }
                if (p.distributors) {
                    if (p.distributors.includes('view')) document.getElementById('ep-perm-distributor-view').checked = true;
                    if (p.distributors.includes('create')) document.getElementById('ep-perm-distributor-create').checked = true;
                    if (p.distributors.includes('edit')) document.getElementById('ep-perm-distributor-edit').checked = true;
                    if (p.distributors.includes('delete')) document.getElementById('ep-perm-distributor-delete').checked = true;
                }
                if (p.staff) {
                    if (p.staff.includes('view')) document.getElementById('ep-perm-staff-view').checked = true;
                    if (p.staff.includes('create')) document.getElementById('ep-perm-staff-create').checked = true;
                    if (p.staff.includes('edit')) document.getElementById('ep-perm-staff-edit').checked = true;
                    if (p.staff.includes('delete')) document.getElementById('ep-perm-staff-delete').checked = true;
                }
                if (p.products) {
                    if (p.products.includes('view')) document.getElementById('ep-perm-product-view').checked = true;
                    if (p.products.includes('create')) document.getElementById('ep-perm-product-create').checked = true;
                    if (p.products.includes('edit')) document.getElementById('ep-perm-product-edit').checked = true;
                    if (p.products.includes('delete')) document.getElementById('ep-perm-product-delete').checked = true;
                }
                if (p.orders) {
                    if (p.orders.includes('view')) document.getElementById('ep-perm-order-view').checked = true;
                    if (p.orders.includes('edit')) document.getElementById('ep-perm-order-edit').checked = true;
                }
                if (p.queries) {
                    if (p.queries.includes('view')) document.getElementById('ep-perm-query-view').checked = true;
                    if (p.queries.includes('edit')) document.getElementById('ep-perm-query-edit').checked = true;
                }
                if (permList) permList.innerHTML = permHtml;
            } catch (e) {
                if (permList) permList.innerHTML = '<span style="color: var(--text-muted); font-style: italic;">Invalid permissions data.</span>';
            }
        } else {
            if (permSection) permSection.style.display = 'none';
        }

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

        if (editMode && typeof window.editStaff === 'function') {
            window.editStaff(userId, user.role);
        } else if (typeof window.closeEditUser === 'function') {
            window.closeEditUser(); 
        }

    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
};
