// SECTION: FETCHING & SPLITTING USER DATA

// Table State Variables
window.allPatientsDoctors = [];
window.filteredPatientsDoctors = [];
window.currentUsersPage = 1;
window.usersPerPage = 10;

window.allStaff = [];
window.filteredStaff = [];
window.currentStaffPage = 1;
window.staffPerPage = 10;

window.allDistributors = [];
window.filteredDistributors = [];
window.currentDistributorsPage = 1;
window.distributorsPerPage = 10;

window.fetchUsers = async function() {
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    const roleFilter = document.getElementById('role-filter') ? document.getElementById('role-filter').value : '';
    
    toggleLoader(true);
    try {
        const response = await fetch(API_ENDPOINTS.USERS, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await response.json();
        toggleLoader(false);
        console.log('[fetchUsers] response data:', data);

        if (!response.ok) throw new Error(data.detail || 'Failed to fetch users list');

        // Toggle create buttons based on permissions
        const btnCreateStaff = document.getElementById('btn-create-staff');
        if (btnCreateStaff) btnCreateStaff.style.display = window.hasPermission('staff', 'create') ? 'inline-block' : 'none';

        const btnCreateUsers = document.getElementById('btn-create-user');
        if (btnCreateUsers) btnCreateUsers.style.display = window.hasPermission('users', 'create') ? 'inline-block' : 'none';

        const btnCreateDist = document.getElementById('btn-create-distributor');
        if (btnCreateDist) btnCreateDist.style.display = window.hasPermission('distributors', 'create') ? 'inline-block' : 'none';

        // 1. Populate User Directory Table (Doctors & Patients)
        const tbodyUsers = document.getElementById('users-table-body');
        if (tbodyUsers) {
            window.allPatientsDoctors = data.filter(u => {
                const isDocOrPat = u.role === 'doctor' || u.role === 'patient';
                if (!isDocOrPat) return false;
                if (roleFilter) return u.role === roleFilter;
                return true;
            });
            
            window.filteredPatientsDoctors = [...window.allPatientsDoctors];
            window.currentUsersPage = 1;
            if (window.renderUsersTable) window.renderUsersTable();
        }

        // 2. Populate Admin Staff Table (Admin & Sub Admin)
        const tbodyStaff = document.getElementById('admin-staff-table-body');
        if (tbodyStaff) {
            window.allStaff = data.filter(u => u.role === 'admin' || u.role === 'sub_admin');
            window.filteredStaff = [...window.allStaff];
            window.currentStaffPage = 1;
            if (window.renderStaffTable) window.renderStaffTable();
        }

        // 3. Populate Distributors Table
        const tbodyDistributors = document.getElementById('distributors-table-body');
        if (tbodyDistributors) {
            window.allDistributors = data.filter(u => u.role === 'distributor');
            window.filteredDistributors = [...window.allDistributors];
            window.currentDistributorsPage = 1;
            if (window.renderDistributorsTable) window.renderDistributorsTable();
        }

    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
}
