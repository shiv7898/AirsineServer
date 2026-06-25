
        let rolesChart = null;

        // Toast Helper
        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            const icon = document.getElementById('toast-icon');
            const msg = document.getElementById('toast-msg');

            msg.textContent = message;
            toast.className = `toast show ${type}`;
            
            if (type === 'success') {
                icon.className = "fa-solid fa-circle-check";
            } else {
                icon.className = "fa-solid fa-triangle-exclamation";
            }

            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }

        // Loader helper
        function toggleLoader(show) {
            document.getElementById('loader').style.display = show ? 'flex' : 'none';
        }

        // Check login on startup
        document.addEventListener('DOMContentLoaded', () => {
            const token = localStorage.getItem('admin_token');
            if (token) {
                // Backfill admin_role from JWT payload if missing (old sessions)
                if (!localStorage.getItem('admin_role')) {
                    try {
                        const payload = JSON.parse(atob(token.split('.')[1]));
                        if (payload.role) localStorage.setItem('admin_role', payload.role);
                    } catch(e) {}
                }
                showDashboard();
            } else {
                showLoginPage();
            }
        });

        // Switch Pages
        function showLoginPage() {
            document.getElementById('auth-page').style.display = 'flex';
            document.getElementById('dashboard-page').style.display = 'none';
        }

        function showDashboard() {
            document.getElementById('auth-page').style.display = 'none';
            document.getElementById('dashboard-page').style.display = 'grid';
            
            // Set user profile initials and display name
            const userJson = localStorage.getItem('admin_user');
            if (userJson) {
                const user = JSON.parse(userJson);
                document.getElementById('user-display-name').textContent = user.name || 'Admin';
                document.getElementById('user-initials').textContent = (user.name || 'AD').split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase();
            }

            applyPermissionNav();
            refreshDashboardData();
        }

        // =========================================================
        //  ROLE-BASED ACCESS CONTROL (RBAC) NAVIGATION
        // =========================================================
        function getPermissions() {
            const role = localStorage.getItem('admin_role');
            if (role === 'super_admin') {
                // Super admin has all permissions
                return {
                    dashboard: ['view'],
                    users: ['view', 'edit', 'delete'],
                    staff: ['view'],
                    products: ['view'],
                    orders: ['view'],
                    queries: ['view']
                };
            }
            // For admin/sub_admin, parse stored permissions JSON
            const userJson = localStorage.getItem('admin_user');
            if (userJson) {
                const user = JSON.parse(userJson);
                if (user.permissions) {
                    try { return JSON.parse(user.permissions); } catch(e) {}
                }
            }
            return {}; // No permissions by default
        }

        function hasPermission(module, action) {
            const perms = getPermissions();
            return perms[module] && perms[module].includes(action);
        }

        function applyPermissionNav() {
            const role = localStorage.getItem('admin_role');

            // Show/hide nav items based on view permission
            const navDash = document.getElementById('nav-dashboard-view');
            const navUsers = document.getElementById('nav-users-view');
            const navStaff = document.getElementById('nav-create-staff-view');
            const navProducts = document.getElementById('nav-products-view');
            const navOrders = document.getElementById('nav-orders-view');
            const navQueries = document.getElementById('nav-queries-view');

            if (navDash) navDash.style.display = hasPermission('dashboard', 'view') ? 'flex' : 'none';
            if (navUsers) navUsers.style.display = hasPermission('users', 'view') ? 'flex' : 'none';
            if (navStaff) navStaff.style.display = hasPermission('staff', 'view') ? 'flex' : 'none';
            if (navProducts) navProducts.style.display = hasPermission('products', 'view') ? 'flex' : 'none';
            if (navOrders) navOrders.style.display = hasPermission('orders', 'view') ? 'flex' : 'none';
            if (navQueries) navQueries.style.display = hasPermission('queries', 'view') ? 'flex' : 'none';

            // Check if there is a path to navigate to, otherwise default to first accessible tab
            routeFromPath();

            if (!document.querySelector('.panel-page.active')) {
                // Navigate to the first accessible tab
                if (hasPermission('dashboard', 'view')) {
                    switchTab('dashboard-view');
                } else if (hasPermission('users', 'view')) {
                    switchTab('users-view');
                } else if (hasPermission('staff', 'view')) {
                    switchTab('create-staff-view');
                } else if (hasPermission('products', 'view')) {
                    switchTab('products-view');
                } else if (hasPermission('orders', 'view')) {
                    switchTab('orders-view');
                } else if (hasPermission('queries', 'view')) {
                    switchTab('queries-view');
                }
            }
        }

        // Handle Login Submission
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            toggleLoader(true);
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();
                toggleLoader(false);

                if (!response.ok) {
                    const errMsg = (data.error && data.error.message) || data.detail || 'Authentication failed';
                    throw new Error(errMsg);
                }

                const allowedRoles = ['super_admin', 'admin', 'sub_admin'];
                if (!allowedRoles.includes(data.role)) {
                    throw new Error('Access Denied. Only Admin users can access this panel.');
                }

                localStorage.setItem('admin_token', data.access_token);
                localStorage.setItem('admin_user', JSON.stringify(data.user));
                localStorage.setItem('admin_role', data.role);

                const greeting = data.role === 'super_admin' ? 'Welcome back, Super Admin!' : `Welcome back, ${data.user.name}!`;
                showToast(greeting);
                showDashboard();
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        });

        // =========================================================
        //  PATH-BASED URL ROUTING
        //  Each page has its own URL: /dashboard | /users | /create-staff
        // =========================================================
        const ROUTE_MAP = {
            '/dashboard':       'dashboard-view',
            '/users':           'users-view',
            '/create-staff':    'create-staff-view',
            '/admin-dashboard': 'dashboard-view',
            '/products-admin':  'products-view',
            '/orders-admin':    'orders-view',
            '/queries-admin':   'queries-view',
        };
        const PATH_MAP = {
            'dashboard-view':    '/dashboard',
            'users-view':        '/users',
            'create-staff-view': '/create-staff',
            'products-view':     '/products-admin',
            'orders-view':       '/orders-admin',
            'queries-view':      '/queries-admin',
        };

        // Tab Navigation (also updates URL hash)
        function switchTab(tabId) {
            document.querySelectorAll('.panel-page').forEach(page => {
                page.classList.remove('active');
            });
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });

            const el = document.getElementById(tabId);
            const nav = document.getElementById(`nav-${tabId}`);
            if (el) el.classList.add('active');
            if (nav) nav.classList.add('active');

            // Update URL path without scrolling
            const path = PATH_MAP[tabId];
            if (path && window.location.pathname !== path) {
                history.pushState(null, '', path);
            }

            if (tabId === 'dashboard-view')    refreshDashboardData();
            else if (tabId === 'users-view')   fetchUsers();
            else if (tabId === 'products-view') fetchProducts();
            else if (tabId === 'orders-view') fetchOrders();
            else if (tabId === 'queries-view') fetchQueries();
        }

        // Navigate to the tab based on current URL path
        function routeFromPath() {
            const token = localStorage.getItem('admin_token');
            if (!token) return; // not logged in, ignore
            const tabId = ROUTE_MAP[window.location.pathname] || null;
            if (tabId) {
                // Only switch if user has permission
                const moduleMap = {
                    'dashboard-view':   ['dashboard', 'view'],
                    'users-view':       ['users', 'view'],
                    'create-staff-view':['staff', 'view'],
                    'products-view':    ['products', 'view'],
                    'orders-view':      ['orders', 'view'],
                    'queries-view':     ['queries', 'view'],
                };
                const [mod, action] = moduleMap[tabId] || [];
                if (mod && hasPermission(mod, action)) {
                    switchTab(tabId);
                    return;
                }
            }
        }

        // Listen for browser back/forward
        window.addEventListener('popstate', () => {
            routeFromPath();
        });


        // Refresh Stats & Dashboard
        async function refreshDashboardData() {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            toggleLoader(true);
            try {
                const response = await fetch('/admin/dashboard', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                toggleLoader(false);

                if (!response.ok) throw new Error(data.detail || 'Failed to fetch dashboard data');

                // Render metrics
                document.getElementById('stat-patients').textContent = data.users.total_patients;
                document.getElementById('stat-doctors').textContent = data.users.total_doctors;
                document.getElementById('stat-distributors').textContent = data.users.total_distributors;
                
                // Admin + sub admin count
                const staffCount = (data.users.total_admins || 0) + (data.users.total_sub_admins || 0);
                document.getElementById('stat-staff').textContent = staffCount;

                // Extra details
                document.getElementById('stat-orders-total').textContent = data.orders.total_orders;
                document.getElementById('stat-products').textContent = data.products.total_products;
                document.getElementById('stat-revenue').textContent = `₹${data.revenue.total_revenue.toLocaleString('en-IN')}`;

                // Setup Chart
                setupChart(data.users);
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        // Role Distribution Chart
        function setupChart(userStats) {
            const ctx = document.getElementById('rolesChart').getContext('2d');
            
            if (rolesChart) {
                rolesChart.destroy();
            }

            rolesChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Patients', 'Doctors', 'Distributors', 'Admins', 'Sub Admins'],
                    datasets: [{
                        data: [
                            userStats.total_patients, 
                            userStats.total_doctors, 
                            userStats.total_distributors, 
                            userStats.total_admins || 0,
                            userStats.total_sub_admins
                        ],
                        backgroundColor: [
                            '#06b6d4', // Patients (Cyan)
                            '#f59e0b', // Doctors (Yellow)
                            '#ec4899', // Distributors (Pink)
                            '#6366f1', // Admins (Indigo)
                            '#10b981'  // Sub Admins (Green)
                        ],
                        borderWidth: 1,
                        borderColor: 'rgba(255, 255, 255, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#94a3b8',
                                font: { family: 'Outfit', size: 12 }
                            }
                        }
                    }
                }
            });
        }

        // Fetch All Users
        async function fetchUsers() {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const roleFilter = document.getElementById('role-filter').value;
            let url = '/admin/users';
            if (roleFilter) {
                url += `?role=${roleFilter}`;
            }

            toggleLoader(true);
            try {
                const response = await fetch(url, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                toggleLoader(false);

                if (!response.ok) throw new Error(data.detail || 'Failed to fetch users list');

                const tbody = document.getElementById('users-table-body');
                tbody.innerHTML = '';

                const canDelete = hasPermission('users', 'delete');
                const canEdit = hasPermission('users', 'edit');

                data.forEach(user => {
                    const row = document.createElement('tr');

                    let actionButtons = '';
                    
                    actionButtons += `<button class="btn-action btn-view" onclick="viewUser(${user.id})" title="View User" style="color: var(--accent-primary);"><i class="fa-solid fa-eye"></i></button>`;

                    if (user.role !== 'super_admin') {
                        if (canEdit) {
                            actionButtons += `<button class="btn-action btn-edit" onclick="editUser(${user.id})" title="Edit User"><i class="fa-solid fa-pen-to-square"></i></button>`;
                        }
                        if (canDelete) {
                            actionButtons += `<button class="btn-action" onclick="deleteUser(${user.id}, '${user.name}')" title="Delete User"><i class="fa-solid fa-trash-can"></i></button>`;
                        }
                    }
                    if (!actionButtons) {
                        actionButtons = `<span style="color: var(--text-muted); font-size: 12px;">N/A</span>`;
                    }

                    row.innerHTML = `
                        <td>${user.id}</td>
                        <td style="font-weight: 500;">${user.name}</td>
                        <td>${user.email}</td>
                        <td><span class="badge ${user.role}">${user.role.replace('_', ' ')}</span></td>
                        <td>${user.phone || 'N/A'}</td>
                        <td>${user.gender || 'N/A'} (${user.age || 'N/A'})</td>
                        <td style="text-align: center;">${actionButtons}</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        // Delete User
        async function deleteUser(userId, userName) {
            if (!confirm(`Are you sure you want to delete user "${userName}"?`)) return;

            const token = localStorage.getItem('admin_token');
            if (!token) return;

            toggleLoader(true);
            try {
                const response = await fetch(`/admin/users/${userId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                toggleLoader(false);

                if (!response.ok) throw new Error(data.detail || 'Failed to delete user');

                showToast(`User "${userName}" has been deleted`);
                fetchUsers();
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        // Create Admin/Sub Admin Staff Account
        document.getElementById('create-staff-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            // Collect permissions from checkboxes
            const permissionsObj = {
                dashboard: [],
                users: [],
                staff: []
            };
            if (document.getElementById('perm-dash-view').checked)   permissionsObj.dashboard.push('view');
            if (document.getElementById('perm-user-view').checked)   permissionsObj.users.push('view');
            if (document.getElementById('perm-user-edit').checked)   permissionsObj.users.push('edit');
            if (document.getElementById('perm-user-delete').checked) permissionsObj.users.push('delete');
            if (document.getElementById('perm-staff-view').checked)  permissionsObj.staff.push('view');

            const staffPayload = {
                name: document.getElementById('staff-name').value,
                email: document.getElementById('staff-email').value,
                password: document.getElementById('staff-password').value,
                role: document.getElementById('staff-role').value,
                phone: document.getElementById('staff-phone').value,
                gender: document.getElementById('staff-gender').value,
                age: document.getElementById('staff-age').value,
                dob: document.getElementById('staff-dob').value,
                homeAddress: document.getElementById('staff-address').value,
                area: document.getElementById('staff-area').value,
                district: document.getElementById('staff-district').value,
                state: document.getElementById('staff-state').value,
                pincode: document.getElementById('staff-pincode').value,
                permissions: JSON.stringify(permissionsObj)
            };

            toggleLoader(true);
            try {
                const response = await fetch('/admin/create-staff', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(staffPayload)
                });

                const data = await response.json();
                toggleLoader(false);

                if (!response.ok) throw new Error(data.detail || 'Failed to create staff member');

                showToast(`Staff account for "${staffPayload.name}" successfully created!`);
                document.getElementById('create-staff-form').reset();
                switchTab('users-view');
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        });



        // Fetch Products
        async function fetchProducts() {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const tbody = document.getElementById('products-table-body');
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading products...</td></tr>';
            
            try {
                const response = await fetch('/admin/products', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch products');
                
                const data = await response.json();
                
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 20px;">No products found</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                data.forEach(p => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>#${p.id}</td>
                        <td style="font-weight: 600;">${p.product_name}</td>
                        <td>₹${p.unit_price} / <span style="text-decoration: line-through; color: var(--text-muted); font-size: 12px;">₹${p.unit_mrp}</span></td>
                        <td><span class="badge" style="background: rgba(34,197,94,0.1); color: var(--accent-success);">${p.customer_discount}%</span></td>
                        <td><span class="badge" style="background: rgba(234,179,8,0.1); color: var(--accent-warning);">${p.distributor_discount}%</span></td>
                        <td><span class="badge" style="background: ${p.is_available ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)'}; color: ${p.is_available ? 'var(--accent-success)' : 'var(--accent-danger)'};">${p.is_available ? 'Active' : 'Inactive'}</span></td>
                        <td style="text-align: center;">
                            <div class="action-btn" title="Edit Product"><i class="fa-solid fa-pen"></i></div>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--accent-danger); padding: 20px;">${err.message}</td></tr>`;
            }
        }

        // Fetch Orders
        async function fetchOrders() {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const tbody = document.getElementById('orders-table-body');
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading orders...</td></tr>';
            
            try {
                const response = await fetch('/admin/orders', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch orders');
                
                const data = await response.json();
                
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 20px;">No orders found</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                data.forEach(o => {
                    const tr = document.createElement('tr');
                    
                    let statusBadge = '';
                    if (o.status === 'PENDING') statusBadge = '<span class="badge" style="background: rgba(234,179,8,0.1); color: var(--accent-warning);">Pending</span>';
                    else if (o.status === 'APPROVED') statusBadge = '<span class="badge" style="background: rgba(59,130,246,0.1); color: #3b82f6;">Approved</span>';
                    else statusBadge = '<span class="badge" style="background: rgba(34,197,94,0.1); color: var(--accent-success);">Delivered</span>';

                    tr.innerHTML = `
                        <td>#${o.id}</td>
                        <td style="font-weight: 600;">${o.customer_name}</td>
                        <td>${o.product_name}</td>
                        <td>${o.quantity}</td>
                        <td style="font-weight: 600; color: var(--accent-primary);">₹${o.final_amount}</td>
                        <td style="color: var(--text-muted); font-size: 13px;">${new Date(o.order_date).toLocaleDateString()}</td>
                        <td>${statusBadge}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--accent-danger); padding: 20px;">${err.message}</td></tr>`;
            }
        }

        // Fetch Queries
        async function fetchQueries() {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const tbody = document.getElementById('queries-table-body');
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading queries...</td></tr>';
            
            try {
                const response = await fetch('/support/admin/queries', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch queries');
                
                const data = await response.json();
                
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 20px;">No queries found</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                data.forEach(q => {
                    const tr = document.createElement('tr');
                    
                    const isResolved = q.status === 'resolved';
                    const statusBadge = isResolved 
                        ? '<span class="badge" style="background: rgba(34,197,94,0.1); color: var(--accent-success);">Resolved</span>' 
                        : '<span class="badge" style="background: rgba(239,68,68,0.1); color: var(--accent-danger);">Pending</span>';

                    const actionBtn = isResolved 
                        ? `<div class="action-btn" title="Resolved" style="opacity: 0.5; cursor: not-allowed;"><i class="fa-solid fa-check-double"></i></div>`
                        : `<div class="action-btn" title="Mark as Resolved" onclick="resolveQuery(${q.id})" style="color: var(--accent-success);"><i class="fa-solid fa-check"></i></div>`;

                    tr.innerHTML = `
                        <td>#${q.id}</td>
                        <td style="font-weight: 600;">${q.user_name}<br><span style="font-size:12px; font-weight: normal; color: var(--text-muted);">${q.user_email}</span></td>
                        <td><span class="badge">${q.user_role}</span></td>
                        <td>${q.query_type}</td>
                        <td style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${q.message}">${q.message}</td>
                        <td>${statusBadge}</td>
                        <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">
                            ${actionBtn}
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--accent-danger); padding: 20px;">${err.message}</td></tr>`;
            }
        }

        async function resolveQuery(queryId) {
            const token = localStorage.getItem('admin_token');
            if (!token) return;
            
            if(!confirm("Mark this query as resolved?")) return;

            toggleLoader(true);
            try {
                const response = await fetch(`/support/admin/queries/${queryId}/resolve`, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                toggleLoader(false);
                if (!response.ok) throw new Error('Failed to resolve query');
                
                showToast('Query marked as resolved!', 'success');
                fetchQueries();
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
            history.pushState(null, '', '/users');
        }

        async function viewUser(userId) {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            toggleLoader(true);
            try {
                const response = await fetch(`/admin/users/${userId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                toggleLoader(false);
                if (!response.ok) throw new Error('Failed to fetch user data');
                
                const user = await response.json();
                
                const contentDiv = document.getElementById('view-user-content');
                contentDiv.innerHTML = `
                    <div style="grid-column: span 2; display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                        <div style="width: 60px; height: 60px; border-radius: 50%; background: var(--accent-primary); color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold;">
                            ${user.name ? user.name.charAt(0).toUpperCase() : '?'}
                        </div>
                        <div>
                            <h3 style="margin: 0; font-size: 20px;">${user.name}</h3>
                            <span class="badge ${user.role}" style="margin-top: 4px; display: inline-block;">${user.role.replace('_', ' ').toUpperCase()}</span>
                        </div>
                    </div>
                    <div><strong>Email:</strong> ${user.email}</div>
                    <div><strong>Phone:</strong> ${user.phone || 'N/A'}</div>
                    <div><strong>Age:</strong> ${user.age || 'N/A'}</div>
                    <div><strong>Gender:</strong> ${user.gender || 'N/A'}</div>
                    <div style="grid-column: span 2;"><strong>Address:</strong> ${user.homeAddress || 'N/A'}</div>
                    
                    ${user.role === 'doctor' ? `
                        <div style="grid-column: span 2; margin-top: 10px;"><strong>Professional Details</strong></div>
                        <div><strong>Hospital:</strong> ${user.hospital || 'N/A'}</div>
                        <div><strong>Specialisation:</strong> ${user.specialisation || 'N/A'}</div>
                        <div><strong>Qualification:</strong> ${user.qualification || 'N/A'}</div>
                        <div><strong>Experience:</strong> ${user.experience ? user.experience + ' Years' : 'N/A'}</div>
                        <div><strong>License Number:</strong> ${user.licenseNumber || 'N/A'}</div>
                    ` : ''}
                    
                    ${user.role === 'distributor' ? `
                        <div style="grid-column: span 2; margin-top: 10px;"><strong>Business Details</strong></div>
                        <div><strong>Company Name:</strong> ${user.companyName || 'N/A'}</div>
                        <div><strong>Business Type:</strong> ${user.businessType || 'N/A'}</div>
                        <div><strong>Distributor Type:</strong> ${user.distributorType || 'N/A'}</div>
                        <div><strong>License Number:</strong> ${user.licenseNumber || 'N/A'}</div>
                    ` : ''}
                `;

                document.getElementById('view-user-modal').style.display = 'flex';
                history.pushState(null, '', \`/admin/users/\${userId}/view\`);
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        // Edit User implementation
        async function editUser(userId) {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            toggleLoader(true);
            try {
                const response = await fetch(`/admin/users/${userId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                toggleLoader(false);
                if (!response.ok) throw new Error('Failed to fetch user data');
                
                const user = await response.json();
                
                document.getElementById('edit-user-id').value = user.id;
                document.getElementById('edit-name').value = user.name || '';
                document.getElementById('edit-email').value = user.email || '';
                document.getElementById('edit-phone').value = user.phone || '';
                document.getElementById('edit-role').value = user.role || 'patient';
                document.getElementById('edit-age').value = user.age || '';
                document.getElementById('edit-gender').value = user.gender || 'Male';
                document.getElementById('edit-address').value = user.homeAddress || '';
                
                document.getElementById('edit-hospital').value = user.hospital || '';
                document.getElementById('edit-specialisation').value = user.specialisation || '';
                document.getElementById('edit-company-name').value = user.companyName || '';
                document.getElementById('edit-license-number').value = user.licenseNumber || '';

                document.getElementById('edit-user-modal').style.display = 'flex';
                history.pushState(null, '', \`/admin/users/\${userId}/edit\`);
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        document.getElementById('edit-user-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const userId = document.getElementById('edit-user-id').value;
            const updatePayload = {
                name: document.getElementById('edit-name').value,
                email: document.getElementById('edit-email').value,
                phone: document.getElementById('edit-phone').value,
                age: parseInt(document.getElementById('edit-age').value) || null,
                gender: document.getElementById('edit-gender').value,
                homeAddress: document.getElementById('edit-address').value,
                hospital: document.getElementById('edit-hospital').value,
                specialisation: document.getElementById('edit-specialisation').value,
                companyName: document.getElementById('edit-company-name').value,
                licenseNumber: document.getElementById('edit-license-number').value
            };

            toggleLoader(true);
            try {
                const response = await fetch(`/admin/users/${userId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(updatePayload)
                });

                toggleLoader(false);
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.detail || 'Failed to update user');
                }

                showToast('User updated successfully', 'success');
                closeModal('edit-user-modal');
                fetchUsers();
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        });

        // Logout
        function handleLogout() {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_user');
            localStorage.removeItem('admin_role');
            showToast('Logged out successfully');
            showLoginPage();
        }
    