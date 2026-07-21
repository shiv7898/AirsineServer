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
            if (window.location.pathname !== '/login') {
                history.pushState(null, '', '/login');
            }
        }

        // =========================================================
        //  MOBILE SIDEBAR TOGGLE
        // =========================================================
        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            sidebar.classList.toggle('open');
            overlay.classList.toggle('show');
        }
        function closeSidebar() {
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if(sidebar) sidebar.classList.remove('open');
            if(overlay) overlay.classList.remove('show');
        }

        function toggleSidebarDesktop() {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.classList.toggle('collapsed');
                
                // Animate chart resize during the sidebar transition for maximum smoothness
                let count = 0;
                const interval = setInterval(() => {
                    if (rolesChart) rolesChart.resize();
                    count++;
                    if (count >= 15) clearInterval(interval);
                }, 20);
                
                setTimeout(() => {
                    window.dispatchEvent(new Event('resize'));
                    if (rolesChart) rolesChart.resize();
                }, 310);
            }
        }

        function toggleProfileDropdown() {
            const dropdown = document.getElementById('profile-dropdown');
            if (dropdown) dropdown.classList.toggle('show');
        }

        document.addEventListener('click', (e) => {
            const profile = document.querySelector('.header-profile');
            const dropdown = document.getElementById('profile-dropdown');
            if (profile && dropdown) {
                if (!profile.contains(e.target)) {
                    dropdown.classList.remove('show');
                }
            }
        });

        function showDashboard() {
            document.getElementById('auth-page').style.display = 'none';
            const dash = document.getElementById('dashboard-page');
            dash.style.display = 'flex';
            dash.style.flexDirection = 'row';
            dash.style.height = '100vh';
            dash.style.overflow = 'hidden';
            
            // Set user profile initials and display name
            const userJson = localStorage.getItem('admin_user');
            if (userJson) {
                const user = JSON.parse(userJson);
                document.getElementById('user-display-name').textContent = user.name || 'Admin';
                document.getElementById('user-initials').textContent = (user.name || 'AD').split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase();
                
                // Populate the new logo area details
                const logoEmail = document.getElementById('sidebar-logo-email');
                if (logoEmail) logoEmail.textContent = user.email || 'admin@airsine.com';
                
                const logoRole = document.getElementById('sidebar-logo-role');
                if (logoRole) {
                    const actualRole = localStorage.getItem('admin_role') || user.role || 'N/A';
                    const roleText = actualRole.replace('_', ' ').toUpperCase();
                    logoRole.textContent = roleText;
                    
                    // Also populate the new profile page
                    const profBadge = document.getElementById('prof-role-badge');
                    if (profBadge) profBadge.textContent = roleText;
                }
                
                const logoId = document.getElementById('sidebar-logo-id');
                if (logoId) logoId.textContent = user.custom_id || 'ID-N/A';

                // Populate new profile view details
                const profAvatar = document.getElementById('prof-avatar');
                if (profAvatar) profAvatar.textContent = (user.name || 'AD').split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase();
                const profName = document.getElementById('prof-name-large');
                if (profName) profName.textContent = user.name || 'User Name';
                const profCustomId = document.getElementById('prof-custom-id');
                if (profCustomId) profCustomId.textContent = user.custom_id || 'N/A';
                const profEmail = document.getElementById('prof-email');
                if (profEmail) profEmail.textContent = user.email || 'N/A';
                const profPhone = document.getElementById('prof-phone');
                if (profPhone) profPhone.textContent = user.phone || 'N/A';
                const profGender = document.getElementById('prof-gender');
                if (profGender) {
                    const age = user.age ? user.age + ' Yrs' : '';
                    const gender = user.gender ? user.gender : '';
                    profGender.textContent = age && gender ? `${age} / ${gender}` : (age || gender || 'N/A');
                }
                const profAddressHome = document.getElementById('prof-address-home');
                if (profAddressHome) profAddressHome.textContent = user.homeAddress || '-';
                const profAddressArea = document.getElementById('prof-address-area');
                if (profAddressArea) profAddressArea.textContent = user.area || '-';
                const profAddressDistrict = document.getElementById('prof-address-district');
                if (profAddressDistrict) profAddressDistrict.textContent = user.district || '-';
                const profAddressState = document.getElementById('prof-address-state');
                if (profAddressState) profAddressState.textContent = user.state || '-';
                const profAddressPincode = document.getElementById('prof-address-pincode');
                if (profAddressPincode) profAddressPincode.textContent = user.pincode || '-';
            }

            applyPermissionNav();
            
            if (window.location.pathname === '/login' || window.location.pathname === '/') {
                switchTab('dashboard-view');
            } else {
                routeFromPath();
                // Fallback to dashboard if route didn't activate a tab
                setTimeout(() => {
                    if (!document.querySelector('.panel-page.active')) {
                        switchTab('dashboard-view');
                    }
                }, 10);
            }
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
                    users: ['view', 'create', 'edit', 'delete'],
                    distributors: ['view', 'create', 'edit', 'delete'],
                    staff: ['view', 'create', 'edit', 'delete'],
                    products: ['view', 'create', 'edit', 'delete'],
                    orders: ['view', 'create', 'edit', 'delete'],
                    queries: ['view', 'create', 'edit', 'delete']
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
            if (module === 'dashboard' && action === 'view') return true;
            const perms = getPermissions();
            return perms[module] && perms[module].includes(action);
        }

        function applyPermissionNav() {
            const role = localStorage.getItem('admin_role');

            // Show/hide nav items based on view permission
            const navDash = document.getElementById('nav-dashboard-view');
            const navUsers = document.getElementById('nav-users-view');
            const navAdminStaff = document.getElementById('nav-admin-staff-view');
            const navDistributors = document.getElementById('nav-distributors-view');
            const navStaff = document.getElementById('nav-create-staff-view');
            const navProducts = document.getElementById('nav-products-view');
            const navCreateProduct = document.getElementById('nav-create-product-view');
            const navOrders = document.getElementById('nav-orders-view');
            const navQueries = document.getElementById('nav-queries-view');

            if (navDash) navDash.style.display = hasPermission('dashboard', 'view') ? 'flex' : 'none';
            if (navUsers) navUsers.style.display = hasPermission('users', 'view') ? 'flex' : 'none';
            if (navAdminStaff) navAdminStaff.style.display = hasPermission('staff', 'view') ? 'flex' : 'none';
            if (navDistributors) navDistributors.style.display = hasPermission('distributors', 'view') ? 'flex' : 'none';
            if (navStaff) navStaff.style.display = hasPermission('staff', 'create') ? 'flex' : 'none';
            if (navProducts) navProducts.style.display = hasPermission('products', 'view') ? 'flex' : 'none';
            if (navCreateProduct) navCreateProduct.style.display = hasPermission('products', 'create') ? 'flex' : 'none';
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
                    switchTab('admin-staff-view');
                } else if (hasPermission('distributors', 'view')) {
                    switchTab('distributors-view');
                } else if (hasPermission('products', 'view')) {
                    switchTab('products-view');
                } else if (hasPermission('orders', 'view')) {
                    switchTab('orders-view');
                } else if (hasPermission('queries', 'view')) {
                    switchTab('queries-view');
                }
            }
        }

        function showAuthModal(title, message) {
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.inset = '0';
            overlay.style.background = 'rgba(15, 23, 42, 0.7)';
            overlay.style.backdropFilter = 'blur(10px)';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';
            overlay.style.zIndex = '99999';
            overlay.style.opacity = '0';
            overlay.style.transition = 'opacity 0.3s ease';

            const modal = document.createElement('div');
            modal.style.background = '#ffffff';
            modal.style.borderRadius = '20px';
            modal.style.padding = '32px 40px';
            modal.style.maxWidth = '400px';
            modal.style.width = '90%';
            modal.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.25)';
            modal.style.textAlign = 'center';
            modal.style.transform = 'translateY(20px) scale(0.95)';
            modal.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

            modal.innerHTML = `
                <div style="width: 60px; height: 60px; background: rgba(239, 68, 68, 0.1); color: #ef4444; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto 20px;">
                    <i class="fa-solid fa-user-lock"></i>
                </div>
                <h3 style="font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 12px; letter-spacing: -0.5px;">${title}</h3>
                <p style="font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 24px;">${message}</p>
                <button id="auth-modal-btn" style="background: linear-gradient(120deg, #ef4444, #dc2626); color: white; border: none; padding: 12px 24px; border-radius: 12px; font-size: 14px; font-weight: 600; cursor: pointer; width: 100%; transition: opacity 0.2s;">Understood</button>
            `;

            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            // Trigger animation
            requestAnimationFrame(() => {
                overlay.style.opacity = '1';
                modal.style.transform = 'translateY(0) scale(1)';
            });

            document.getElementById('auth-modal-btn').addEventListener('click', () => {
                overlay.style.opacity = '0';
                modal.style.transform = 'translateY(20px) scale(0.95)';
                setTimeout(() => overlay.remove(), 300);
            });
        }

        // Handle Login Submission
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            toggleLoader(true);
            try {
                const response = await fetch('/web/user/login', {
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
                if (err.message.includes("Account Access Suspended")) {
                    showAuthModal("Account Suspended", err.message);
                } else {
                    showToast(err.message, 'error');
                }
            }
        });

        // =========================================================
        //  PATH-BASED URL ROUTING
        //  Each page has its own URL: /dashboard | /users | /create-staff
        // =========================================================
        const ROUTE_MAP = {
            '/dashboard':       'dashboard-view',
            '/users':           'users-view',
            '/admin-staff':     'admin-staff-view',
            '/distributors':    'distributors-view',
            '/create-staff':    'create-staff-view',
            '/create-user':     'create-user-view',
            '/create-product':  'create-product-view',
            '/admin-dashboard': 'dashboard-view',
            '/products-admin':  'products-view',
            '/orders-admin':    'orders-view',
            '/queries-admin':   'queries-view',
            '/profile':         'my-profile-view'
        };
        const PATH_MAP = {
            'dashboard-view':    '/dashboard',
            'users-view':        '/users',
            'admin-staff-view':  '/admin-staff',
            'distributors-view': '/distributors',
            'create-staff-view': '/create-staff',
            'create-user-view':  '/create-user',
            'create-product-view': '/create-product',
            'products-view':     '/products-admin',
            'orders-view':       '/orders-admin',
            'queries-view':      '/queries-admin',
            'my-profile-view':   '/profile',
            'user-detail-view':  '/profile'
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

            // Auto-close sidebar on mobile after navigating
            if (window.innerWidth <= 768) closeSidebar();

            // Update URL path without scrolling
            const path = PATH_MAP[tabId];
            if (path && window.location.pathname !== path) {
                if (tabId === 'user-detail-view' && window.location.pathname.startsWith('/user-view/')) {
                    // Do nothing, preserve the specific user view path in the address bar
                } else {
                    history.pushState(null, '', path);
                }
            }

            if (tabId === 'dashboard-view')    refreshDashboardData();
            else if (tabId === 'users-view')   fetchUsers();
            else if (tabId === 'admin-staff-view') fetchUsers();
            else if (tabId === 'distributors-view') fetchUsers();
            else if (tabId === 'products-view') fetchProducts();
            else if (tabId === 'orders-view') fetchOrders();
            else if (tabId === 'queries-view') fetchQueries();
        }

        // Navigate to the tab based on current URL path
        function routeFromPath() {
            const token = localStorage.getItem('admin_token');
            if (!token) return; // not logged in, ignore

            if (window.location.pathname.startsWith('/user-view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[2]) { viewUser(parts[2], false); return; }
            }
            if (window.location.pathname.startsWith('/user-edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[2]) { viewUser(parts[2], true); return; }
            }
            if (window.location.pathname.startsWith('/staff-view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[2]) { viewUser(parts[2], false); return; }
            }
            if (window.location.pathname.startsWith('/staff-edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[2]) { viewUser(parts[2], true); return; }
            }
            if (window.location.pathname.startsWith('/distributor-view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[2]) { viewUser(parts[2], false); return; }
            }
            if (window.location.pathname.startsWith('/distributor-edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[2]) { viewUser(parts[2], true); return; }
            }

            const tabId = ROUTE_MAP[window.location.pathname] || null;
            if (tabId) {
                // Only switch if user has permission
                const moduleMap = {
                    'dashboard-view':   ['dashboard', 'view'],
                    'users-view':       ['users', 'view'],
                    'admin-staff-view': ['staff', 'view'],
                    'distributors-view': ['distributors', 'view'],
                    'create-staff-view':['staff', 'view'],
                    'create-user-view':  ['users', 'view'],
                    'create-product-view': ['products', 'view'],
                    'products-view':    ['products', 'view'],
                    'orders-view':      ['orders', 'view'],
                    'queries-view':     ['queries', 'view'],
                };
                if (tabId === 'my-profile-view') {
                    switchTab(tabId);
                    return;
                }
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
                const response = await fetch('/web/admin/dashboard', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                toggleLoader(false);

                if (!response.ok) throw new Error(data.detail || 'Failed to fetch dashboard data');

                // Render metrics
                document.getElementById('stat-patients').textContent = data.users.total_patients;
                document.getElementById('stat-doctors').textContent = data.users.total_doctors;
                document.getElementById('stat-distributors').textContent = data.users.total_distributors;
                
                // Admin + sub admin + super admin count
                const staffCount = (data.users.total_admins || 0) + (data.users.total_sub_admins || 0) + (data.users.total_super_admins || 0);
                document.getElementById('stat-staff').textContent = staffCount;

                // Extra details
                document.getElementById('stat-orders-total').textContent = data.orders.total_orders;
                document.getElementById('stat-products').textContent = data.products.total_products;
                
                const patProdEl = document.getElementById('stat-pat-products');
                if (patProdEl) patProdEl.textContent = data.products.patient_products || 0;
                
                const distProdEl = document.getElementById('stat-dist-products');
                if (distProdEl) distProdEl.textContent = data.products.distributor_products || 0;

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
                    labels: ['Patients', 'Doctors', 'Distributors', 'Admins', 'Sub Admins', 'Super Admins'],
                    datasets: [{
                        data: [
                            userStats.total_patients || 0, 
                            userStats.total_doctors || 0, 
                            userStats.total_distributors || 0, 
                            userStats.total_admins || 0,
                            userStats.total_sub_admins || 0,
                            userStats.total_super_admins || 0
                        ],
                        backgroundColor: [
                            '#06b6d4', // Patients (Cyan)
                            '#f59e0b', // Doctors (Yellow)
                            '#ec4899', // Distributors (Pink)
                            '#6366f1', // Admins (Indigo)
                            '#10b981', // Sub Admins (Green)
                            '#ef4444'  // Super Admins (Red)
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

        // Fetch All Users & Populate Split Tables
        async function fetchUsers() {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const roleFilter = document.getElementById('role-filter') ? document.getElementById('role-filter').value : '';
            
            toggleLoader(true);
            try {
                const response = await fetch('/web/admin/users', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                toggleLoader(false);
                console.log('[fetchUsers] response data:', data);

                if (!response.ok) throw new Error(data.detail || 'Failed to fetch users list');

                const canDelete = hasPermission('users', 'delete');
                const canEdit = hasPermission('users', 'edit');
                console.log('[fetchUsers] permissions - canEdit:', canEdit, 'canDelete:', canDelete);

                // Helper to create initials avatar
                const getAvatarHtml = (user) => {
                    const initials = (user.name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
                    const colors = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];
                    const colorIndex = (user.name || 'U').charCodeAt(0) % colors.length;
                    const avatarBg = colors[colorIndex];
                    return `<div style="display: flex; align-items: center; gap: 12px;">
                        <div style="width: 32px; height: 32px; border-radius: 50%; background-color: ${avatarBg}; color: white; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">${initials}</div>
                        <span>${user.name}</span>
                    </div>`;
                };

                // Helper to build action buttons
                const getActionsHtml = (user) => {
                    let actionButtons = '';
                    actionButtons += `<button class="btn-action btn-view" onclick="viewUser(${user.id}, false, '${user.role}')" title="View User" style="color: var(--accent-primary);"><i class="fa-solid fa-eye"></i></button>`;
                    if (user.role !== 'super_admin') {
                        if (canEdit) {
                            actionButtons += `<button class="btn-action btn-edit" onclick="editUser(${user.id}, '${user.role}')" title="Edit User"><i class="fa-solid fa-pen-to-square"></i></button>`;
                        }
                        if (canDelete) {
                            actionButtons += `<button class="btn-action" onclick="deleteUser(${user.id}, '${user.name}', '${user.role}')" title="Delete User"><i class="fa-solid fa-trash-can"></i></button>`;
                        }
                    }
                    return actionButtons || `<span style="color: var(--text-muted); font-size: 12px;">N/A</span>`;
                };

                // 1. Populate User Directory Table (Doctors & Patients)
                const tbodyUsers = document.getElementById('users-table-body');
                if (tbodyUsers) {
                    tbodyUsers.innerHTML = '';
                    const filteredUsers = data.filter(u => {
                        const isDocOrPat = u.role === 'doctor' || u.role === 'patient';
                        if (!isDocOrPat) return false;
                        if (roleFilter) return u.role === roleFilter;
                        return true;
                    });
                    console.log('[fetchUsers] Patient/Doctor count:', filteredUsers.length);
                    
                    filteredUsers.forEach((user, index) => {
                        const row = document.createElement('tr');
                        const srNo = filteredUsers.length - index;
                        row.innerHTML = `
                            <td style="font-weight: 600; color: var(--text-muted);">${srNo}</td>
                            <td style="font-family: monospace; font-weight: 600;">${user.custom_id || user.id}</td>
                            <td style="font-weight: 500;">${getAvatarHtml(user)}</td>
                            <td>${user.email}</td>
                            <td><span class="badge ${user.role || ''}">${(user.role || 'N/A').replace('_', ' ')}</span></td>
                            <td>${user.phone || 'N/A'}</td>
                            <td>${user.gender || 'N/A'} (${user.age || 'N/A'})</td>
                            <td style="text-align: center;">${getActionsHtml(user)}</td>
                        `;
                        tbodyUsers.appendChild(row);
                    });
                }

                // 2. Populate Admin Staff Table (Admin & Sub Admin)
                const tbodyStaff = document.getElementById('admin-staff-table-body');
                if (tbodyStaff) {
                    tbodyStaff.innerHTML = '';
                    const filteredStaff = data.filter(u => u.role === 'admin' || u.role === 'sub_admin');
                    console.log('[fetchUsers] Admin Staff count:', filteredStaff.length);
                    
                    filteredStaff.forEach((user, index) => {
                        const row = document.createElement('tr');
                        const srNo = filteredStaff.length - index;
                        row.innerHTML = `
                            <td style="font-weight: 600; color: var(--text-muted);">${srNo}</td>
                            <td style="font-family: monospace; font-weight: 600;">${user.custom_id || user.id}</td>
                            <td style="font-weight: 500;">${getAvatarHtml(user)}</td>
                            <td>${user.email}</td>
                            <td><span class="badge ${user.role || ''}">${(user.role || 'N/A').replace('_', ' ')}</span></td>
                            <td>${user.phone || 'N/A'}</td>
                            <td style="text-align: center;">${getActionsHtml(user)}</td>
                        `;
                        tbodyStaff.appendChild(row);
                    });
                }

                // 3. Populate Distributors Table
                const tbodyDistributors = document.getElementById('distributors-table-body');
                if (tbodyDistributors) {
                    tbodyDistributors.innerHTML = '';
                    const filteredDist = data.filter(u => u.role === 'distributor');
                    console.log('[fetchUsers] Distributors count:', filteredDist.length);
                    
                    filteredDist.forEach((user, index) => {
                        const row = document.createElement('tr');
                        const srNo = filteredDist.length - index;
                        row.innerHTML = `
                            <td style="font-weight: 600; color: var(--text-muted);">${srNo}</td>
                            <td style="font-family: monospace; font-weight: 600;">${user.custom_id || user.id}</td>
                            <td style="font-weight: 500; font-family: Outfit; font-weight: 600; color: var(--text-primary);">${user.companyName || 'N/A'}</td>
                            <td style="font-weight: 500;">${getAvatarHtml(user)}</td>
                            <td><span class="badge ${user.distributorType ? 'sub_admin' : 'patient'}">${user.distributorType || 'N/A'}</span></td>
                            <td>${user.email}</td>
                            <td>${user.phone || 'N/A'}</td>
                            <td style="font-weight: 600; color: var(--accent-success);">${user.commission !== undefined ? user.commission + '%' : '0%'}</td>
                            <td style="text-align: center;">${getActionsHtml(user)}</td>
                        `;
                        tbodyDistributors.appendChild(row);
                    });
                }

                // Toggle top bar button based on permission
                const btnCreateUser = document.getElementById('btn-create-user');
                if(btnCreateUser) btnCreateUser.style.display = hasPermission('users', 'create') ? 'inline-block' : 'none';

            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        // Delete User
        async function deleteUser(userId, userName, role = null) {
            if (!confirm(`Are you sure you want to delete user "${userName}"?`)) return;

            const token = localStorage.getItem('admin_token');
            if (!token) return;

            toggleLoader(true);
            try {
                const url = role ? `/web/admin/users/${userId}?role=${role}` : `/web/admin/users/${userId}`;
                const response = await fetch(url, {
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

        // ---- Create Standard User helpers ----
        function openCreateUserForm() {
            switchTab('create-user-view');
            updateCreateUserForm();
            updateRolePills();
        }

        function closeCreateUserForm() {
            switchTab('users-view');
            document.getElementById('create-standard-user-form').reset();
            document.getElementById('doctor-fields').style.display = 'none';
            document.getElementById('distributor-fields').style.display = 'none';
            // Reset role pills
            document.querySelector('input[name="role-pill"][value="patient"]').checked = true;
            document.getElementById('c-role').value = 'patient';
            updateRolePills();
        }

        function updateRolePills() {
            const role = document.getElementById('c-role').value;
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
                el.querySelector('div:last-child').style.color = isActive ? c.color : '#64748b';
            });
        }

        function updateCreateUserForm() {
            const role = document.getElementById('c-role').value;
            document.getElementById('doctor-fields').style.display      = (role === 'doctor')      ? 'block' : 'none';
            document.getElementById('distributor-fields').style.display = (role === 'distributor') ? 'block' : 'none';
        }

        // Close modal when clicking backdrop (guard: element may not exist)
        const _createUserModal = document.getElementById('create-user-modal');
        if (_createUserModal) {
            _createUserModal.addEventListener('click', function(e) {
                if (e.target === this) closeCreateUserForm();
            });
        }


        async function submitCreateUser(e) {
            e.preventDefault();
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const role = document.getElementById('c-role').value;
            const dobVal = document.getElementById('c-dob').value;

            const payload = {
                name:        document.getElementById('c-name').value.trim(),
                email:       document.getElementById('c-email').value.trim(),
                password:    document.getElementById('c-password').value,
                phone:       document.getElementById('c-phone').value.trim(),
                role:        role,
                gender:      document.getElementById('c-gender').value,
                age:         parseInt(document.getElementById('c-age').value),
                dob:         dobVal || '01-01-2000',
                homeAddress: document.getElementById('c-address').value.trim() || 'N/A',
                area:        document.getElementById('c-area').value.trim()    || 'N/A',
                district:    document.getElementById('c-district').value.trim()|| 'N/A',
                state:       document.getElementById('c-state').value.trim()   || 'N/A',
                pincode:     document.getElementById('c-pincode').value.trim(),
            };

            // Doctor-specific fields
            if (role === 'doctor') {
                payload.hospital       = document.getElementById('c-hospital').value.trim()        || null;
                payload.specialisation = document.getElementById('c-specialisation').value.trim()  || null;
                payload.qualification  = document.getElementById('c-qualification').value.trim()   || null;
                payload.experience     = document.getElementById('c-experience').value || null;
            }

            // Distributor-specific fields
            if (role === 'distributor') {
                payload.companyName      = document.getElementById('c-company').value.trim()           || null;
                payload.businessType     = document.getElementById('c-business-type').value.trim()    || null;
                payload.licenseNumber    = document.getElementById('c-license').value.trim()          || null;
            }

            toggleLoader(true);
            try {
                const response = await fetch('/web/admin/users', {
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
                switchTab('users-view');
                fetchUsers();
                document.getElementById('create-standard-user-form').reset();
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        // Create Admin/Sub Admin Staff Account
        document.getElementById('create-staff-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = localStorage.getItem('admin_token');
            if (!token) {
                showToast('Session expired. Please login again.', 'error');
                setTimeout(() => { localStorage.clear(); showLoginPage(); }, 1500);
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
            if (document.getElementById('perm-dash-view').checked)     permissionsObj.dashboard.push('view');
            if (document.getElementById('perm-user-view').checked)     permissionsObj.users.push('view');
            if (document.getElementById('perm-user-create') && document.getElementById('perm-user-create').checked) permissionsObj.users.push('create');
            if (document.getElementById('perm-user-edit').checked)     permissionsObj.users.push('edit');
            if (document.getElementById('perm-user-delete').checked)   permissionsObj.users.push('delete');
            if (document.getElementById('perm-distributor-view').checked)     permissionsObj.distributors.push('view');
            if (document.getElementById('perm-distributor-create') && document.getElementById('perm-distributor-create').checked) permissionsObj.distributors.push('create');
            if (document.getElementById('perm-distributor-edit').checked)     permissionsObj.distributors.push('edit');
            if (document.getElementById('perm-distributor-delete').checked)   permissionsObj.distributors.push('delete');
            if (document.getElementById('perm-staff-view').checked)    permissionsObj.staff.push('view');
            if (document.getElementById('perm-staff-create') && document.getElementById('perm-staff-create').checked) permissionsObj.staff.push('create');
            if (document.getElementById('perm-product-view').checked)  permissionsObj.products.push('view');
            if (document.getElementById('perm-product-create') && document.getElementById('perm-product-create').checked) permissionsObj.products.push('create');
            if (document.getElementById('perm-product-edit').checked)  permissionsObj.products.push('edit');
            if (document.getElementById('perm-product-delete').checked)permissionsObj.products.push('delete');
            if (document.getElementById('perm-order-view').checked)    permissionsObj.orders.push('view');
            if (document.getElementById('perm-order-edit').checked)    permissionsObj.orders.push('edit');
            if (document.getElementById('perm-query-view').checked)    permissionsObj.queries.push('view');
            if (document.getElementById('perm-query-edit').checked)    permissionsObj.queries.push('edit');

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
                const response = await fetch('/web/admin/create-staff', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(staffPayload)
                });

                const data = await response.json();
                toggleLoader(false);
                console.log('[create-staff] response:', response.status, data);

                if (!response.ok) {
                    // Handle different error response shapes
                    const errMsg = (data.error && data.error.message)
                        || (Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : data.detail)
                        || 'Failed to create staff member';
                    throw new Error(errMsg);
                }

                showToast(`✅ Staff account for "${staffPayload.name}" successfully created!`);
                document.getElementById('create-staff-form').reset();
                switchTab('users-view');
                fetchUsers();
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
                console.error('[create-staff] error:', err.message);
            }
        });


        let adminProducts = [];

        // Fetch Products
        async function fetchProducts() {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const tbody = document.getElementById('products-table-body');
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading products...</td></tr>';
            
            try {
                const response = await fetch('/web/admin/products', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) {
                    let errMsg = 'Failed to fetch products';
                    try {
                        const errData = await response.json();
                        errMsg = errData.detail || errData.message || errMsg;
                    } catch(e) {}
                    throw new Error(errMsg);
                }
                
                const data = await response.json();
                console.log("Products Data:", data);
                adminProducts = data;
                
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No products found</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                data.forEach(p => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>#${p.id}</td>
                        <td>
                            <div style="font-weight: 600;">${p.product_name}</div>
                            <div style="font-size: 11px; color: var(--text-muted);">${p.product_type}</div>
                        </td>
                        <td>
                            <div style="font-weight: 600;">${p.brand || '-'}</div>
                            <div style="font-size: 11px; color: var(--text-muted);">${p.model_name || '-'}</div>
                        </td>
                        <td>
                            <div style="font-weight: 600;">₹${p.selling_price || p.unit_mrp}</div>
                            <div style="font-size: 11px; color: var(--text-muted); text-decoration: line-through;">₹${p.unit_mrp}</div>
                        </td>
                        <td>
                            <span class="badge" style="background: ${p.target_audience === 'distributor' ? 'rgba(236, 72, 153, 0.1)' : 'rgba(139,92,246,0.1)'}; color: ${p.target_audience === 'distributor' ? '#db2777' : '#8b5cf6'}; text-transform: capitalize;">
                                ${p.target_audience === 'patient_doctor' ? 'Patient & Doctor' : (p.target_audience || 'All')}
                            </span>
                        </td>
                        <td style="font-weight: 600; color: ${p.stock_pieces > 0 ? 'var(--text-dark)' : 'var(--accent-danger)'};">${p.stock_pieces} pcs</td>
                        <td><span class="badge" style="background: ${p.product_status === 'Active' ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)'}; color: ${p.product_status === 'Active' ? 'var(--accent-success)' : 'var(--accent-danger)'};">${p.product_status || (p.is_available ? 'Active' : 'Inactive')}</span></td>
                        <td style="text-align: center;">
                            ${hasPermission('products', 'view') ? `<div class="btn-action" title="View Product" onclick="openViewProductPage(${p.id})"><i class="fa-solid fa-eye"></i></div>` : ''}
                            ${hasPermission('products', 'edit') ? `<div class="btn-action" title="Edit Product" onclick="openEditProductPage(${p.id})"><i class="fa-solid fa-pen"></i></div>` : ''}
                            ${hasPermission('products', 'delete') ? `<div class="btn-action delete" title="Delete Product" onclick="deleteProduct(${p.id})"><i class="fa-solid fa-trash"></i></div>` : ''}
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--accent-danger); padding: 20px;">${err.message}</td></tr>`;
            }
        }
        
        async function deleteProduct(id) {
            if (!confirm('Are you sure you want to delete this product?')) return;
            const token = localStorage.getItem('admin_token');
            if (!token) return showToast('Session expired, please login again.', 'error');
            
            try {
                const response = await fetch(`/web/products/${id}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (!response.ok) {
                    let errMsg = 'Failed to delete product';
                    try {
                        const errData = await response.json();
                        errMsg = errData.detail || errData.message || errMsg;
                    } catch(e) {}
                    throw new Error(errMsg);
                }
                
                showToast('Product deleted successfully', 'success');
                fetchProducts(); // Refresh the table
            } catch (err) {
                showToast(err.message, 'error');
            }
        }

        // Preview Product Modal Logic
        function openProductPreviewModal(e) {
            e.preventDefault();
            
            const name = document.getElementById('cp-name').value;
            const type = document.getElementById('cp-type').value;
            const mrp = parseFloat(document.getElementById('cp-mrp').value) || 0;
            const discount = parseFloat(document.getElementById('cp-discount').value) || 0;
            let sellingPrice = parseFloat(document.getElementById('cp-selling-price').value);
            const gst = parseFloat(document.getElementById('cp-gst').value) || 0;
            
            if (isNaN(sellingPrice)) {
                sellingPrice = mrp - (mrp * discount / 100);
            }
            
            const totalGstAmount = (sellingPrice * gst) / 100;
            const finalAmount = sellingPrice + totalGstAmount;

            const previewHtml = `
                <div style="background: #f8fafc; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 12px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 14px;">Product Name</span>
                        <span style="font-weight: 600; color: #0f172a;">${name}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 14px;">Product Type</span>
                        <span style="font-weight: 600; color: #0f172a;">${type}</span>
                    </div>
                    <hr style="border: none; border-top: 1px dashed #cbd5e1; margin: 4px 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 14px;">Unit MRP</span>
                        <span style="font-weight: 600; color: #0f172a;">₹${mrp.toFixed(2)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 14px;">Discount</span>
                        <span style="font-weight: 600; color: #ef4444;">${discount}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 14px;">Selling Price</span>
                        <span style="font-weight: 600; color: #0f172a;">₹${sellingPrice.toFixed(2)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-size: 14px;">Tax/GST (${gst}%)</span>
                        <span style="font-weight: 600; color: #0f172a;">+ ₹${totalGstAmount.toFixed(2)}</span>
                    </div>
                    <hr style="border: none; border-top: 1px dashed #cbd5e1; margin: 4px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #64748b; font-size: 16px; font-weight: 600;">Total Final Amount</span>
                        <span style="font-weight: 800; color: #10b981; font-size: 24px;">₹${finalAmount.toFixed(2)}</span>
                    </div>
                </div>
            `;
            
            document.getElementById('preview-content').innerHTML = previewHtml;
            document.getElementById('product-preview-modal').style.display = 'flex';
        }

        // Submit Create Product (Called from Modal)
        async function confirmAndSubmitProduct() {
            const token = localStorage.getItem('admin_token');
            if (!token) return showToast('Session expired, please login again.', 'error');

            const name = document.getElementById('cp-name').value;
            const type = document.getElementById('cp-type').value;
            const brand = document.getElementById('cp-brand').value;
            const model = document.getElementById('cp-model').value;
            const mrp = document.getElementById('cp-mrp').value;
            const discount = document.getElementById('cp-discount').value;
            const sellingPrice = document.getElementById('cp-selling-price').value;
            const refDiscount = document.getElementById('cp-ref-discount').value;
            const gst = document.getElementById('cp-gst').value;
            const stock = document.getElementById('cp-stock').value;
            const status = document.getElementById('cp-status').value;
            const desc = document.getElementById('cp-desc').value;
            const target = document.getElementById('cp-target').value;
            
            const imageFiles = document.getElementById('cp-image').files;

            const formData = new FormData();
            formData.append('product_name', name);
            formData.append('product_type', type);
            if (brand) formData.append('brand', brand);
            if (model) formData.append('model_name', model);
            formData.append('unit_mrp', mrp);
            if (discount) formData.append('discount', discount);
            if (sellingPrice) formData.append('selling_price', sellingPrice);
            if (refDiscount) formData.append('referral_discount', refDiscount);
            if (gst) formData.append('tax_gst', gst);
            if (stock) formData.append('stock_pieces', stock);
            formData.append('product_status', status);
            if (desc) formData.append('description', desc);
            
            if (imageFiles && imageFiles.length > 0) {
                for (let i = 0; i < imageFiles.length; i++) {
                    formData.append('images', imageFiles[i]);
                }
            }

            const endpoint = target === 'distributor' ? '/mobile/distributor/add-product' : '/web/products/add-product';

            toggleLoader(true);
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });

                if (response.ok) {
                    showToast('Product created successfully!');
                    closeModal('product-preview-modal');
                    
                    // Save values before reset
                    const lastGst = document.getElementById('cp-gst').value;
                    const lastType = document.getElementById('cp-type').value;
                    if (lastGst) localStorage.setItem('last_product_gst', lastGst);
                    if (lastType) localStorage.setItem('last_product_type', lastType);
                    
                    document.getElementById('create-product-form').reset();
                    
                    // Restore after reset
                    const savedGst = localStorage.getItem('last_product_gst');
                    const savedType = localStorage.getItem('last_product_type');
                    if (savedGst) document.getElementById('cp-gst').value = savedGst;
                    if (savedType) document.getElementById('cp-type').value = savedType;
                    
                    switchTab('products-view');
                } else {
                    const err = await response.json();
                    showToast(err.detail || 'Failed to create product', 'error');
                }
            } catch (error) {
                console.error(error);
                showToast('Network error while creating product', 'error');
            } finally {
                toggleLoader(false);
            }
        }

        function openEditProductPage(productId) {
            const product = adminProducts.find(p => p.id === productId);
            if (!product) {
                showToast('Product not found in data.', 'error');
                return;
            }
            
            document.getElementById('ep-id').value = product.id;
            document.getElementById('ep-target').value = product.target_audience || 'patient_doctor';
            document.getElementById('ep-name').value = product.product_name || '';
            document.getElementById('ep-type').value = product.product_type || '';
            document.getElementById('ep-brand').value = product.brand || '';
            document.getElementById('ep-model').value = product.model_name || '';
            document.getElementById('ep-mrp').value = product.unit_mrp || '';
            document.getElementById('ep-discount').value = product.discount || 0;
            document.getElementById('ep-selling-price').value = product.selling_price || '';
            document.getElementById('ep-ref-discount').value = product.referral_discount || 0;
            document.getElementById('ep-gst').value = product.tax_gst || 0;
            document.getElementById('ep-stock').value = product.stock_pieces || 0;
            document.getElementById('ep-status').value = product.product_status || (product.is_available ? 'Active' : 'Inactive');
            document.getElementById('ep-desc').value = product.description || '';
            
            switchTab('edit-product-view');
        }

        async function submitEditProduct(e) {
            e.preventDefault();
            const token = localStorage.getItem('admin_token');
            if (!token) return showToast('Session expired, please login again.', 'error');
            
            const productId = document.getElementById('ep-id').value;
            const target = document.getElementById('ep-target').value;
            
            const formData = new FormData();
            formData.append('product_name', document.getElementById('ep-name').value);
            formData.append('product_type', document.getElementById('ep-type').value);
            formData.append('brand', document.getElementById('ep-brand').value);
            formData.append('model_name', document.getElementById('ep-model').value);
            formData.append('unit_mrp', document.getElementById('ep-mrp').value);
            formData.append('discount', document.getElementById('ep-discount').value || 0);
            formData.append('selling_price', document.getElementById('ep-selling-price').value);
            formData.append('referral_discount', document.getElementById('ep-ref-discount').value || 0);
            formData.append('tax_gst', document.getElementById('ep-gst').value || 0);
            formData.append('stock_pieces', document.getElementById('ep-stock').value || 0);
            formData.append('product_status', document.getElementById('ep-status').value);
            formData.append('description', document.getElementById('ep-desc').value);
            
            const imageFiles = document.getElementById('ep-image').files;
            if (imageFiles && imageFiles.length > 0) {
                for (let i = 0; i < imageFiles.length; i++) {
                    formData.append('images', imageFiles[i]);
                }
            }

            const endpoint = target === 'distributor' ? `/mobile/distributor/update-product/${productId}` : `/web/products/update-product/${productId}`;

            toggleLoader(true);
            try {
                const response = await fetch(endpoint, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });

                if (response.ok) {
                    showToast('Product updated successfully!', 'success');
                    switchTab('products-view');
                    fetchProducts();
                } else {
                    const err = await response.json();
                    showToast(err.detail || 'Failed to update product', 'error');
                }
            } catch (error) {
                console.error(error);
                showToast('Network error while updating product', 'error');
            } finally {
                toggleLoader(false);
            }
        }

        function openViewProductPage(productId) {
            const product = adminProducts.find(p => p.id === productId);
            if (!product) {
                showToast('Product not found in data.', 'error');
                return;
            }
            
            const container = document.getElementById('view-product-container');
            container.innerHTML = `
                <div style="width: 100%;">
                    <!-- Section: Product Info -->
                    <div style="background: #fff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                        <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: #94a3b8; margin-bottom: 18px; display: flex; align-items: center; gap: 8px;">
                            <i class="fa-solid fa-circle-info" style="color: #6366f1;"></i> Product Information
                        </div>
                        <div class="cp-grid-3">
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Product For</label>
                                <input type="text" disabled value="${product.target_audience === 'distributor' ? 'Distributor' : 'Patient / Doctor'}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Product Name</label>
                                <input type="text" disabled value="${product.product_name || ''}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Product Type</label>
                                <input type="text" disabled value="${product.product_type || ''}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Brand</label>
                                <input type="text" disabled value="${product.brand || ''}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Model Name</label>
                                <input type="text" disabled value="${product.model_name || ''}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Images</label>
                                <div style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;background:#f8fafc;color:#64748b;">${product.product_images ? 'Images available' : 'No images'}</div>
                            </div>
                        </div>
                    </div>

                    <!-- Section: Pricing & Discounts -->
                    <div style="background: #fff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                        <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: #94a3b8; margin-bottom: 18px; display: flex; align-items: center; gap: 8px;">
                            <i class="fa-solid fa-indian-rupee-sign" style="color: #10b981;"></i> Pricing & Discounts
                        </div>
                        <div class="cp-grid-3">
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Unit MRP (₹)</label>
                                <input type="text" disabled value="${product.unit_mrp || '0.00'}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Discount (%)</label>
                                <input type="text" disabled value="${product.discount || '0.0'}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Selling Price (₹)</label>
                                <input type="text" disabled value="${product.selling_price || product.unit_mrp || '0.00'}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Referral Discount (%)</label>
                                <input type="text" disabled value="${product.referral_discount || '0.0'}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Tax/GST (%)</label>
                                <input type="text" disabled value="${product.tax_gst || '0.0'}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Total Stock Pieces</label>
                                <input type="text" disabled value="${product.stock_pieces || '0'}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                            <div>
                                <label style="display:block;font-size:12px;font-weight:600;color:#64748b;margin-bottom:6px;">Status</label>
                                <input type="text" disabled value="${product.product_status || (product.is_available ? 'Active' : 'Inactive')}" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;background:#f8fafc;color:#64748b;font-family:inherit;">
                            </div>
                        </div>
                    </div>

                    <!-- Section: Description -->
                    <div style="background: #fff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                        <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: #94a3b8; margin-bottom: 18px; display: flex; align-items: center; gap: 8px;">
                            <i class="fa-solid fa-align-left" style="color: #f59e0b;"></i> Description
                        </div>
                        <div>
                            <textarea disabled rows="4" style="width:100%;border:1.5px solid #e2e8f0;border-radius:10px;padding:11px 14px;font-size:14px;outline:none;resize:none;background:#f8fafc;color:#64748b;font-family:inherit;">${product.description || 'No description available.'}</textarea>
                        </div>
                    </div>
                </div>
            `;
            switchTab('view-product-view');
        }

        // Fetch Orders
        async function fetchOrders() {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            const tbody = document.getElementById('orders-table-body');
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading orders...</td></tr>';
            
            try {
                const response = await fetch('/web/admin/orders', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch orders');
                
                const data = await response.json();
                console.log("Orders Data:", data);
                
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
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading queries...</td></tr>';
            
            try {
                const response = await fetch('/web/support/admin/queries', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch queries');
                
                const data = await response.json();
                console.log("Queries Data:", data);
                
                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No queries found</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                data.forEach(q => {
                    const tr = document.createElement('tr');
                    
                    const isResolved = q.status === 'resolved';
                    const statusBadge = isResolved 
                        ? '<span class="badge" style="background: rgba(34,197,94,0.1); color: var(--accent-success);">Resolved</span>' 
                        : '<span class="badge" style="background: rgba(239,68,68,0.1); color: var(--accent-danger);">Pending</span>';

                    const resolveBtn = isResolved 
                        ? `<div class="btn-action" title="Resolved" style="opacity: 0.5; cursor: not-allowed;"><i class="fa-solid fa-check-double"></i></div>`
                        : `<div class="btn-action" title="Mark as Resolved" onclick="resolveQuery(${q.id})" style="color: var(--accent-success);"><i class="fa-solid fa-check"></i></div>`;

                    let imageThumbnail = `<span style="color: var(--text-muted); font-size: 13px; font-style: italic;">None</span>`;
                    
                    if (q.image) {
                        const imagesArray = q.image.split(',');
                        const firstImage = imagesArray[0];
                        const countBadge = imagesArray.length > 1 
                            ? `<div style="position: absolute; top: -5px; right: -5px; background: var(--accent-primary); color: white; border-radius: 50%; width: 20px; height: 20px; font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">+${imagesArray.length - 1}</div>` 
                            : '';
                        
                        imageThumbnail = `<div style="position: relative; width: 44px; height: 44px; margin: 0 auto; cursor: pointer;" onclick="viewQueryImage('${q.image}')" title="Click to view ${imagesArray.length} image(s)">
                            <div style="width: 100%; height: 100%; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-glass); box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='scale(1.15)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.05)'">
                                <img src="/uploads/support/${firstImage}" style="width: 100%; height: 100%; object-fit: cover;" />
                            </div>
                            ${countBadge}
                        </div>`;
                    }

                    tr.innerHTML = `
                        <td>#${q.id}</td>
                        <td style="font-weight: 600;">${q.user_name}<br><span style="font-size:12px; font-weight: normal; color: var(--text-muted);">${q.user_email}</span></td>
                        <td><span class="badge">${q.user_role}</span></td>
                        <td>${q.query_type}</td>
                        <td style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${q.message}">${q.message}</td>
                        <td style="text-align: center;">${imageThumbnail}</td>
                        <td>${statusBadge}</td>
                        <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">
                            ${resolveBtn}
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
                const response = await fetch(`/web/support/admin/queries/${queryId}/resolve`, {
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
            // Only push state for user modals if needed, to avoid breaking query view
            if (modalId === 'view-user-modal' || modalId === 'edit-user-modal') {
                history.pushState(null, '', '/users');
            }
        }

        let currentImageIndex = 0;
        let currentImagesArray = [];

        function viewQueryImage(imageString) {
            currentImagesArray = imageString.split(',');
            currentImageIndex = 0;
            updateImageDisplay();
            document.getElementById('image-viewer-modal').style.display = 'flex';
        }

        function updateImageDisplay() {
            const img = document.getElementById('query-image-display');
            img.src = '/uploads/support/' + currentImagesArray[currentImageIndex];
            
            const counter = document.getElementById('image-counter');
            if (currentImagesArray.length > 1) {
                counter.style.display = 'block';
                counter.innerText = `${currentImageIndex + 1} / ${currentImagesArray.length}`;
            } else {
                counter.style.display = 'none';
            }

            document.getElementById('prev-img-btn').style.display = currentImagesArray.length > 1 ? 'flex' : 'none';
            document.getElementById('next-img-btn').style.display = currentImagesArray.length > 1 ? 'flex' : 'none';
        }

        function nextImage() {
            if (currentImageIndex < currentImagesArray.length - 1) {
                currentImageIndex++;
            } else {
                currentImageIndex = 0; // wrap
            }
            updateImageDisplay();
        }

        function prevImage() {
            if (currentImageIndex > 0) {
                currentImageIndex--;
            } else {
                currentImageIndex = currentImagesArray.length - 1; // wrap
            }
            updateImageDisplay();
        }

        function setUdField(viewId, editId, value, isSelect) {
            const vEl = document.getElementById(viewId);
            const eEl = document.getElementById(editId);
            const displayVal = (value !== null && value !== undefined && value !== '') ? value : null;
            if (vEl) { vEl.textContent = displayVal || 'N/A'; vEl.className = 'ud-value' + (displayVal ? '' : ' na'); }
            if (eEl) {
                if (isSelect) { [...eEl.options].forEach(o => o.selected = o.value === value || o.text === value); }
                else { eEl.value = displayVal || ''; }
            }
        }

        let originalUserData = null; // Store globally so we can cancel edit
        let detailBackTab = 'users-view'; // Store globally to handle back button destination

        function goBackFromDetail() {
            switchTab(detailBackTab);
        }

        async function viewUser(userId, editMode = false, role = null) {
            const token = localStorage.getItem('admin_token');
            if (!token) return;

            // Auto-infer role if not provided
            if (!role) {
                if (window.location.pathname.startsWith('/user-view/') || window.location.pathname.startsWith('/user-edit/')) {
                    role = 'patient';
                } else if (window.location.pathname.startsWith('/staff-view/') || window.location.pathname.startsWith('/staff-edit/')) {
                    role = 'admin';
                } else if (window.location.pathname.startsWith('/distributor-view/') || window.location.pathname.startsWith('/distributor-edit/')) {
                    role = 'distributor';
                }
            }

            toggleLoader(true);
            try {
                const url = role ? `/web/admin/users/${userId}/view?role=${role}` : `/web/admin/users/${userId}/view`;
                const response = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
                toggleLoader(false);
                if (!response.ok) throw new Error('Failed to fetch user data');
                const user = await response.json();
                originalUserData = user; // cache it

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
                setUdField('v-name', 'e-name', user.name);
                setUdField('v-phone', 'e-phone', user.phone);
                setUdField('v-email', 'e-email', user.email);
                setUdField('v-gender', 'e-gender', user.gender, true);
                setUdField('v-dob', 'e-dob', user.dob);
                setUdField('v-age', 'e-age', user.age);
                setUdField('v-role', 'e-role', user.role);
                setUdField('v-status', 'e-status', user.status || 'Active', true);
                setUdField('v-verification', 'e-verification', user.verificationStatus || 'Pending', true);
                setUdField('v-commission', 'e-commission', user.commission);
                setUdField('v-discount-field', 'e-discount', user.discount);

                setUdField('v-address', 'e-address', user.homeAddress);
                setUdField('v-area', 'e-area', user.area);
                setUdField('v-state', 'e-state', user.state);
                setUdField('v-district', 'e-district', user.district);
                setUdField('v-pincode', 'e-pincode', user.pincode);

                // 3. Dynamic role-specific fields
                const roleSection = document.getElementById('ud-role-section');
                const roleTitle = document.getElementById('ud-role-section-title');
                const roleFields = document.getElementById('ud-role-fields');

                if (user.role === 'doctor') {
                    roleSection.style.display = 'block';
                    roleTitle.innerHTML = '<i class="fa-solid fa-stethoscope" style="color: var(--accent-primary);"></i> Doctor Professional Details';
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
                } else if (user.role === 'distributor') {
                    roleSection.style.display = 'block';
                    roleTitle.innerHTML = '<i class="fa-solid fa-building" style="color: var(--accent-primary);"></i> Distributor Company Details';
                    roleFields.innerHTML = `
                        <div class="ud-field">
                            <div class="ud-label">Company Name</div>
                            <div class="ud-value" id="v-companyName">${user.companyName || 'N/A'}</div>
                            <input class="ud-input" id="e-companyName" type="text" style="display:none;" value="${user.companyName || ''}">
                        </div>
                        <div class="ud-field">
                            <div class="ud-label">Business Type</div>
                            <div class="ud-value" id="v-businessType">${user.businessType || 'N/A'}</div>
                            <input class="ud-input" id="e-businessType" type="text" style="display:none;" value="${user.businessType || ''}">
                        </div>
                        <div class="ud-field">
                            <div class="ud-label">Distributor Type</div>
                            <div class="ud-value" id="v-distributorType">${user.distributorType || 'N/A'}</div>
                            <input class="ud-input" id="e-distributorType" type="text" style="display:none;" value="${user.distributorType || ''}">
                        </div>
                        <div class="ud-field">
                            <div class="ud-label">License Number</div>
                            <div class="ud-value" id="v-licenseNumber">${user.licenseNumber || 'N/A'}</div>
                            <input class="ud-input" id="e-licenseNumber" type="text" style="display:none;" value="${user.licenseNumber || ''}">
                        </div>
                    `;
                } else {
                    roleSection.style.display = 'none';
                    roleFields.innerHTML = '';
                }

                // 4. Permissions section
                // Reset edit permissions checkboxes
                const permCheckboxes = [
                    'ep-perm-user-view', 'ep-perm-user-create', 'ep-perm-user-edit', 'ep-perm-user-delete',
                    'ep-perm-distributor-view', 'ep-perm-distributor-create', 'ep-perm-distributor-edit', 'ep-perm-distributor-delete',
                    'ep-perm-staff-view', 'ep-perm-staff-create',
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
                if ((user.role === 'admin' || user.role === 'sub_admin') && user.permissions) {
                    permSection.style.display = 'block';
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
                    } catch (e) {
                        permHtml = '<span style="color: var(--text-muted); font-style: italic;">Error parsing permissions.</span>';
                    }
                    permList.innerHTML = permHtml;
                } else {
                    permSection.style.display = 'none';
                    permList.innerHTML = '';
                }

                // 5. Dynamic show/hide of metrics cards & basic info fields based on user role
                const metricsContainer = document.getElementById('ud-metrics-container');
                const ordersCard = document.getElementById('ud-orders-card');
                const commissionCard = document.getElementById('ud-commission-card');
                const discountCard = document.getElementById('ud-discount-card');
                const referralCard = document.getElementById('ud-referral-card');
                const commField = document.getElementById('ud-commission-field-container');
                const discField = document.getElementById('ud-discount-field-container');

                const isAdmin = ['super_admin', 'admin', 'sub_admin'].includes(user.role);
                const isPatientOrDoctor = ['patient', 'doctor'].includes(user.role);
                const isDistributor = user.role === 'distributor';

                if (isAdmin) {
                    if (metricsContainer) metricsContainer.style.display = 'none';
                    if (commField) commField.style.display = 'none';
                    if (discField) discField.style.display = 'none';
                } else if (isPatientOrDoctor) {
                    if (metricsContainer) metricsContainer.style.display = 'grid';
                    if (ordersCard) ordersCard.style.display = 'none';
                    if (commissionCard) commissionCard.style.display = 'none';
                    if (discountCard) discountCard.style.display = 'none';
                    if (referralCard) referralCard.style.display = 'flex';
                    if (commField) commField.style.display = 'none';
                    if (discField) discField.style.display = 'none';
                } else if (isDistributor) {
                    if (metricsContainer) metricsContainer.style.display = 'grid';
                    if (ordersCard) ordersCard.style.display = 'flex';
                    if (commissionCard) commissionCard.style.display = 'flex';
                    if (discountCard) discountCard.style.display = 'flex';
                    if (referralCard) referralCard.style.display = 'flex';
                    if (commField) commField.style.display = 'flex';
                    if (discField) discField.style.display = 'flex';
                }

                // Make sure we are in static view mode or edit mode based on editMode
                if (editMode) {
                    enableDetailEdit();
                } else {
                    cancelDetailEdit();
                }

                // Switch to tab
                switchTab('user-detail-view');
                
                // Dynamically determine URLs and back tab destination
                let viewUrl = '';
                let editUrl = '';
                if (['super_admin', 'admin', 'sub_admin'].includes(user.role)) {
                    detailBackTab = 'admin-staff-view';
                    viewUrl = `/staff-view/${userId}`;
                    editUrl = `/staff-edit/${userId}`;
                } else if (user.role === 'distributor') {
                    detailBackTab = 'distributors-view';
                    viewUrl = `/distributor-view/${userId}`;
                    editUrl = `/distributor-edit/${userId}`;
                } else {
                    detailBackTab = 'users-view';
                    viewUrl = `/user-view/${userId}`;
                    editUrl = `/user-edit/${userId}`;
                }

                // Update URL history pathname
                history.pushState(null, '', editMode ? editUrl : viewUrl);
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        function enableDetailEdit() {
            // Hide all .ud-value divs
            document.querySelectorAll('#user-detail-view .ud-value').forEach(el => el.style.display = 'none');
            // Show all .ud-input fields
            document.querySelectorAll('#user-detail-view .ud-input').forEach(el => el.style.display = 'block');
            
            // Adjust buttons visibility
            const editBtn = document.getElementById('detail-edit-btn');
            if (editBtn) editBtn.style.display = 'none';
            document.getElementById('detail-save-btn').style.display = 'inline-flex';
            document.getElementById('detail-cancel-btn').style.display = 'inline-flex';

            // Show/hide permissions edit section
            const loggedInRole = localStorage.getItem('admin_role');
            const isSuperAdmin = loggedInRole === 'super_admin';
            const editedRole = originalUserData ? originalUserData.role : '';
            const isEditedAdmin = ['admin', 'sub_admin'].includes(editedRole);

            if (isSuperAdmin && isEditedAdmin) {
                const permSection = document.getElementById('ud-permissions-section');
                if (permSection) permSection.style.display = 'none';
                const permEditSection = document.getElementById('ud-permissions-edit-section');
                if (permEditSection) permEditSection.style.display = 'block';
            }
        }

        function cancelDetailEdit() {
            // Restore original input values from Cache
            if (originalUserData) {
                const user = originalUserData;
                setUdField('v-name', 'e-name', user.name);
                setUdField('v-phone', 'e-phone', user.phone);
                setUdField('v-email', 'e-email', user.email);
                setUdField('v-gender', 'e-gender', user.gender, true);
                setUdField('v-dob', 'e-dob', user.dob);
                setUdField('v-age', 'e-age', user.age);
                setUdField('v-role', 'e-role', user.role);
                setUdField('v-status', 'e-status', user.status || 'Active', true);
                setUdField('v-verification', 'e-verification', user.verificationStatus || 'Pending', true);
                setUdField('v-commission', 'e-commission', user.commission);
                setUdField('v-discount-field', 'e-discount', user.discount);

                setUdField('v-address', 'e-address', user.homeAddress);
                setUdField('v-area', 'e-area', user.area);
                setUdField('v-state', 'e-state', user.state);
                setUdField('v-district', 'e-district', user.district);
                setUdField('v-pincode', 'e-pincode', user.pincode);

                // Role fields
                const eHosp = document.getElementById('e-hospital'); if(eHosp) eHosp.value = user.hospital || '';
                const eSpec = document.getElementById('e-specialisation'); if(eSpec) eSpec.value = user.specialisation || '';
                const eQual = document.getElementById('e-qualification'); if(eQual) eQual.value = user.qualification || '';
                const eExp = document.getElementById('e-experience'); if(eExp) eExp.value = user.experience || '';

                const eComp = document.getElementById('e-companyName'); if(eComp) eComp.value = user.companyName || '';
                const eBus = document.getElementById('e-businessType'); if(eBus) eBus.value = user.businessType || '';
                const eDist = document.getElementById('e-distributorType'); if(eDist) eDist.value = user.distributorType || '';
                const eLic = document.getElementById('e-licenseNumber'); if(eLic) eLic.value = user.licenseNumber || '';
            }

            // Show all .ud-value divs
            document.querySelectorAll('#user-detail-view .ud-value').forEach(el => el.style.display = 'flex');
            // Hide all .ud-input fields
            document.querySelectorAll('#user-detail-view .ud-input').forEach(el => el.style.display = 'none');
            
            // Adjust buttons visibility
            const editBtn = document.getElementById('detail-edit-btn');
            if (editBtn) editBtn.style.display = 'inline-flex';
            document.getElementById('detail-save-btn').style.display = 'none';
            document.getElementById('detail-cancel-btn').style.display = 'none';

            // Reset permission sections visibility
            const permEditSection = document.getElementById('ud-permissions-edit-section');
            if (permEditSection) permEditSection.style.display = 'none';

            const editedRole = originalUserData ? originalUserData.role : '';
            const isEditedAdmin = ['admin', 'sub_admin'].includes(editedRole);
            const permSection = document.getElementById('ud-permissions-section');
            if (isEditedAdmin && permSection) {
                permSection.style.display = 'block';
            }
        }

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

            // Build permissions if current user is super_admin and edited user is admin/sub_admin
            const loggedInRole = localStorage.getItem('admin_role');
            const isSuperAdmin = loggedInRole === 'super_admin';
            const editedRole = originalUserData ? originalUserData.role : '';
            const isEditedAdmin = ['admin', 'sub_admin'].includes(editedRole);

            if (isSuperAdmin && isEditedAdmin) {
                const epPermissions = {
                    dashboard: ['view'], // dashboard view is always allowed
                    users: [],
                    distributors: [],
                    staff: [],
                    products: [],
                    orders: [],
                    queries: []
                };
                
                if (document.getElementById('ep-perm-user-view').checked) epPermissions.users.push('view');
                if (document.getElementById('ep-perm-user-create').checked) epPermissions.users.push('create');
                if (document.getElementById('ep-perm-user-edit').checked) epPermissions.users.push('edit');
                if (document.getElementById('ep-perm-user-delete').checked) epPermissions.users.push('delete');
                
                if (document.getElementById('ep-perm-distributor-view').checked) epPermissions.distributors.push('view');
                if (document.getElementById('ep-perm-distributor-create').checked) epPermissions.distributors.push('create');
                if (document.getElementById('ep-perm-distributor-edit').checked) epPermissions.distributors.push('edit');
                if (document.getElementById('ep-perm-distributor-delete').checked) epPermissions.distributors.push('delete');
                
                if (document.getElementById('ep-perm-staff-view').checked) epPermissions.staff.push('view');
                if (document.getElementById('ep-perm-staff-create').checked) epPermissions.staff.push('create');
                
                if (document.getElementById('ep-perm-product-view').checked) epPermissions.products.push('view');
                if (document.getElementById('ep-perm-product-create').checked) epPermissions.products.push('create');
                if (document.getElementById('ep-perm-product-edit').checked) epPermissions.products.push('edit');
                if (document.getElementById('ep-perm-product-delete').checked) epPermissions.products.push('delete');
                
                if (document.getElementById('ep-perm-order-view').checked) epPermissions.orders.push('view');
                if (document.getElementById('ep-perm-order-edit').checked) epPermissions.orders.push('edit');
                
                if (document.getElementById('ep-perm-query-view').checked) epPermissions.queries.push('view');
                if (document.getElementById('ep-perm-query-edit').checked) epPermissions.queries.push('edit');
                
                payload.permissions = JSON.stringify(epPermissions);
            }

            // Read role-specific inputs dynamically
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
                const editedRole = originalUserData ? originalUserData.role : '';
                const url = editedRole ? `/web/admin/users/${userId}/edit?role=${editedRole}` : `/web/admin/users/${userId}/edit`;
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
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to save edits');
                }

                showToast('✅ User updated successfully!', 'success');
                // Reload user detail view with updated values
                viewUser(userId);
            } catch (err) {
                toggleLoader(false);
                showToast(err.message, 'error');
            }
        }

        // Edit User implementation
        async function editUser(userId, role = null) {
            await viewUser(userId, true, role);
        }

        async function viewAndEdit(userId, role = null) {
            await viewUser(userId, true, role);
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

            // Build permissions if current user is super_admin and edited user is admin/sub_admin
            const isSuperAdmin = localStorage.getItem('admin_role') === 'super_admin';
            if (isSuperAdmin && originalUserData && ['admin', 'sub_admin'].includes(originalUserData.role)) {
                const perms = {};
                document.querySelectorAll('.edit-perm-cb').forEach(cb => {
                    const mod = cb.dataset.module;
                    const action = cb.dataset.action;
                    if (cb.checked) {
                        if (!perms[mod]) perms[mod] = [];
                        perms[mod].push(action);
                    }
                });
                updatePayload.permissions = JSON.stringify(perms);
            }

            toggleLoader(true);
            try {
                const roleParam = originalUserData ? originalUserData.role : '';
                const url = roleParam ? `/web/admin/users/${userId}/edit?role=${roleParam}` : `/web/admin/users/${userId}/edit`;
                const response = await fetch(url, {
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
        // Password Hide/Show Logic
        document.addEventListener('DOMContentLoaded', () => {
            const togglePwdBtn = document.querySelector('.show-pwd');
            const pwdInput = document.getElementById('login-password');
            if(togglePwdBtn && pwdInput) {
                togglePwdBtn.addEventListener('click', () => {
                    if (pwdInput.type === 'password') {
                        pwdInput.type = 'text';
                        togglePwdBtn.textContent = 'HIDE';
                    } else {
                        pwdInput.type = 'password';
                        togglePwdBtn.textContent = 'SHOW';
                    }
                });
            }
            
            // Restore last used Product Type and Tax/GST
            const savedGst = localStorage.getItem('last_product_gst');
            if (savedGst) {
                const cpGst = document.getElementById('cp-gst');
                if (cpGst) cpGst.value = savedGst;
            }
            const savedType = localStorage.getItem('last_product_type');
            if (savedType) {
                const cpType = document.getElementById('cp-type');
                if (cpType) cpType.value = savedType;
            }
        });