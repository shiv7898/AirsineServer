// ============================================================================
// SHARED USER UTILITIES & ROUTER
// ============================================================================

window.getAvatarHtml = (user) => {
    const initials = (user.name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    const colors = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];
    const colorIndex = (user.name || 'U').charCodeAt(0) % colors.length;
    const avatarBg = colors[colorIndex];
    return `<div style="display: flex; align-items: center; gap: 12px;">
        <div style="width: 32px; height: 32px; border-radius: 10px; background: linear-gradient(135deg, ${avatarBg}22, ${avatarBg}11); color: ${avatarBg}; border: 1px solid ${avatarBg}33; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">${initials}</div>
        <div style="font-weight: 800; color: #059669; font-size: 12px; letter-spacing: -0.2px;">${user.name}</div>
    </div>`;
};

window.getActionsHtml = (user) => {
    let moduleName = 'users';
    if (user.role === 'admin' || user.role === 'sub_admin') moduleName = 'staff';
    else if (user.role === 'distributor') moduleName = 'distributors';

    const uCanEdit = window.hasPermission(moduleName, 'edit');
    const uCanDelete = window.hasPermission(moduleName, 'delete');

    let actionButtons = '';
    actionButtons += `<button class="btn-action" onclick="viewUser(${user.id}, false, '${user.role}')" title="View User" style="color: #3b82f6; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2);"><i class="fa-solid fa-eye"></i></button>`;
    if (user.role !== 'super_admin') {
        if (uCanEdit) {
            actionButtons += `<button class="btn-action" onclick="viewUser(${user.id}, true, '${user.role}')" title="Edit User" style="color: #f59e0b; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2);"><i class="fa-solid fa-pen-to-square"></i></button>`;
        }
        if (uCanDelete) {
            actionButtons += `<button class="btn-action" onclick="deleteUser(${user.id}, '${user.name}', '${user.role}')" title="Delete User" style="color: #ef4444; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2);"><i class="fa-solid fa-trash-can"></i></button>`;
        }
    }
    return actionButtons || `<span style="color: var(--text-muted); font-size: 12px;">N/A</span>`;
};

// ============================================================================
// GLOBAL ROUTERS FOR CRUD (To keep backwards compatibility with HTML files)
// ============================================================================

window.viewUser = (id, editMode, role) => {
    if (!role) {
        const path = window.location.pathname;
        if (path.includes('/distributors/')) role = 'distributor';
        else if (path.includes('/admin-staff/')) role = 'admin';
        else role = 'patient';
    }

    let moduleUrl = 'users';
    if (role === 'admin' || role === 'sub_admin') moduleUrl = 'admin-staff';
    else if (role === 'distributor') moduleUrl = 'distributors';
    
    const action = editMode ? 'edit' : 'view';
    const newPath = `/${moduleUrl}/${action}/${id}`;
    if (window.location.pathname !== newPath) {
        history.pushState(null, '', newPath);
    }

    if (role === 'distributor' && window.viewDistributor) {
        return window.viewDistributor(id, editMode);
    }
    if ((role === 'admin' || role === 'sub_admin') && window.viewStaff) {
        return window.viewStaff(id, editMode, role);
    }
    if (window.viewPatientDoctor) {
        return window.viewPatientDoctor(id, editMode, role);
    }
    console.error('viewUser router: Function for role', role, 'not found');
};

window.editUser = (id, role) => {
    if (role === 'distributor' && window.editDistributor) {
        return window.editDistributor(id);
    }
    if ((role === 'admin' || role === 'sub_admin') && window.editStaff) {
        return window.editStaff(id, role);
    }
    if (window.editPatientDoctor) {
        return window.editPatientDoctor(id, role);
    }
    console.error('editUser router: Function for role', role, 'not found');
};

window.triggerEditMode = () => {
    if (!window.originalUserData) return;
    
    let moduleUrl = 'users';
    const role = window.originalUserData.role;
    if (role === 'admin' || role === 'sub_admin') moduleUrl = 'admin-staff';
    else if (role === 'distributor') moduleUrl = 'distributors';
    
    const newPath = `/${moduleUrl}/edit/${window.originalUserData.id}`;
    if (window.location.pathname !== newPath) {
        history.pushState(null, '', newPath);
    }
    
    window.editUser(window.originalUserData.id, role);
};

window.deleteUser = (id, name, role) => {
    if (role === 'distributor' && window.deleteDistributor) {
        return window.deleteDistributor(id, name);
    }
    if ((role === 'admin' || role === 'sub_admin') && window.deleteStaff) {
        return window.deleteStaff(id, name, role);
    }
    if (window.deletePatientDoctor) {
        return window.deletePatientDoctor(id, name, role);
    }
    console.error('deleteUser router: Function for role', role, 'not found');
};

window.submitUpdateUserRole = function() {
    if (!window.originalUserData) return;
    const role = window.originalUserData.role;
    
    if (role === 'distributor' && window.submitUpdateDistributorRole) {
        return window.submitUpdateDistributorRole();
    }
    if ((role === 'admin' || role === 'sub_admin') && window.submitUpdateStaffRole) {
        return window.submitUpdateStaffRole();
    }
    if (window.submitUpdatePatientDoctorRole) {
        return window.submitUpdatePatientDoctorRole();
    }
};

