        // SECTION 4: AUTHENTICATION & LOGIN
        // ============================================================================
        
        // Handle Login Submission
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            toggleLoader(true);
            try {
                const response = await fetch(API_ENDPOINTS.LOGIN, {
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
            '/create-distributor': 'create-distributor-view',
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
            'create-distributor-view': '/create-distributor',
            'create-product-view': '/create-product',
            'products-view':     '/products-admin',
            'orders-view':       '/orders-admin',
            'view-order-view':   '/orders/view',
            'edit-order-view':   '/orders/edit',
            'queries-view':      '/queries-admin',
            'view-query-view':   '/queries/view',
            'edit-query-view':   '/queries/edit',
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

            // Attach scroll listener for header animation
            if (typeof attachScrollListener === 'function') attachScrollListener(tabId);

            // Update URL path without scrolling
            const path = PATH_MAP[tabId];
            if (path && window.location.pathname !== path) {
                if (tabId === 'user-detail-view' && window.location.pathname.match(/\/(users|distributors|admin-staff)\/(view|edit)\/\d+/)) {
                    // Do nothing, preserve the specific user view path in the address bar
                } else if ((tabId === 'view-order-view' || tabId === 'edit-order-view' || tabId === 'view-product-view' || tabId === 'edit-product-view') && window.location.pathname.match(/\/(orders|products)\/(view|edit)\/\d+/)) {
                    // Do nothing, preserve the specific order/product view path
                } else {
                    history.pushState(null, '', path);
                }
            }

            // Dynamically adjust hero background height and border-radius
            const heroBg = document.getElementById('main-hero-bg');
            if (heroBg) {
                if (tabId === 'dashboard-view') {
                    heroBg.style.height = '280px';
                    heroBg.style.borderBottomLeftRadius = '40px';
                    heroBg.style.borderBottomRightRadius = '40px';
                } else {
                    heroBg.style.height = '85px';
                    heroBg.style.borderBottomLeftRadius = '0px';
                    heroBg.style.borderBottomRightRadius = '0px';
                }
            }

            if (tabId === 'dashboard-view')    refreshDashboardData();
            else if (tabId === 'users-view')   fetchUsers();
            else if (tabId === 'admin-staff-view') fetchUsers();
            else if (tabId === 'distributors-view') fetchUsers();
            else if (tabId === 'products-view') fetchProducts();
            else if (tabId === 'orders-view') fetchOrders();
            else if (tabId === 'queries-view') fetchQueries();
            else if (tabId === 'create-user-view') {
                const lblPatient = document.getElementById('label-role-patient');
                const lblDoctor = document.getElementById('label-role-doctor');
                const lblDistributor = document.getElementById('label-role-distributor');
                
                const canCreateUsers = window.hasPermission('users', 'create');
                const canCreateDist = window.hasPermission('distributors', 'create');
                const canCreateStaff = window.hasPermission('staff', 'create');
                if (lblPatient) lblPatient.style.display = canCreateUsers ? 'block' : 'none';
                if (lblDoctor) lblDoctor.style.display = canCreateUsers ? 'block' : 'none';
                if (lblDistributor) lblDistributor.style.display = canCreateDist ? 'block' : 'none';

                const currentRoleInput = document.getElementById('c-role');
                if (currentRoleInput) {
                    let role = currentRoleInput.value || 'patient';
                    if (role === 'distributor' && !canCreateDist && canCreateUsers) {
                        currentRoleInput.value = 'patient';
                    } else if ((role === 'patient' || role === 'doctor') && !canCreateUsers && canCreateDist) {
                        currentRoleInput.value = 'distributor';
                    }
                    const radioToSelect = document.querySelector(`input[name="role-pill"][value="${currentRoleInput.value}"]`);
                    if (radioToSelect) radioToSelect.checked = true;
                    if (typeof updateCreateUserForm === 'function') updateCreateUserForm();
                    if (typeof updateRolePills === 'function') updateRolePills();
                }
            }
        }

        // Navigate to the tab based on current URL path
        function routeFromPath() {
            const token = localStorage.getItem('admin_token');
            if (!token) return; // not logged in, ignore

            if (window.location.pathname.startsWith('/users/view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) { viewUser(parts[3], false); return; }
            }
            if (window.location.pathname.startsWith('/users/edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) { viewUser(parts[3], true); return; }
            }
            if (window.location.pathname.startsWith('/admin-staff/view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) { viewUser(parts[3], false); return; }
            }
            if (window.location.pathname.startsWith('/admin-staff/edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) { viewUser(parts[3], true); return; }
            }
            if (window.location.pathname.startsWith('/distributors/view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) { viewUser(parts[3], false); return; }
            }
            if (window.location.pathname.startsWith('/distributors/edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) { viewUser(parts[3], true); return; }
            }
            if (window.location.pathname.startsWith('/orders/view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) {
                    const id = parseInt(parts[3]);
                    switchTab('orders-view');
                    setTimeout(() => {
                        if (window.adminOrders && window.adminOrders.length > 0) {
                            if (window.openViewOrderPage) window.openViewOrderPage(id);
                        } else if (window.fetchOrders) {
                            window.fetchOrders().then(() => {
                                if (window.openViewOrderPage) window.openViewOrderPage(id);
                            });
                        }
                    }, 200);
                    return;
                }
            }
            if (window.location.pathname.startsWith('/orders/edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) {
                    const id = parseInt(parts[3]);
                    switchTab('orders-view');
                    setTimeout(() => {
                        if (window.adminOrders && window.adminOrders.length > 0) {
                            if (window.openEditOrderPage) window.openEditOrderPage(id);
                        } else if (window.fetchOrders) {
                            window.fetchOrders().then(() => {
                                if (window.openEditOrderPage) window.openEditOrderPage(id);
                            });
                        }
                    }, 200);
                    return;
                }
            }
            if (window.location.pathname.startsWith('/queries/view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) {
                    const id = parseInt(parts[3]);
                    switchTab('queries-view');
                    setTimeout(() => {
                        if (window.queriesDataCache && window.queriesDataCache.length > 0) {
                            if (window.openViewQueryPage) window.openViewQueryPage(id);
                        } else if (window.fetchQueries) {
                            window.fetchQueries().then(() => {
                                if (window.openViewQueryPage) window.openViewQueryPage(id);
                            });
                        }
                    }, 200);
                    return;
                }
            }
            if (window.location.pathname.startsWith('/queries/edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) {
                    const id = parseInt(parts[3]);
                    switchTab('queries-view');
                    setTimeout(() => {
                        if (window.queriesDataCache && window.queriesDataCache.length > 0) {
                            if (window.openEditQueryPage) window.openEditQueryPage(id);
                        } else if (window.fetchQueries) {
                            window.fetchQueries().then(() => {
                                if (window.openEditQueryPage) window.openEditQueryPage(id);
                            });
                        }
                    }, 200);
                    return;
                }
            }
            if (window.location.pathname.startsWith('/products/view/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) {
                    const id = parseInt(parts[3]);
                    switchTab('products-view');
                    setTimeout(() => {
                        if (window.adminProducts && window.adminProducts.length > 0) {
                            if (window.openViewProductPage) window.openViewProductPage(id);
                        } else if (window.fetchProducts) {
                            window.fetchProducts().then(() => {
                                if (window.openViewProductPage) window.openViewProductPage(id);
                            });
                        }
                    }, 200);
                    return;
                }
            }
            if (window.location.pathname.startsWith('/products/edit/')) {
                const parts = window.location.pathname.split('/');
                if (parts[3]) {
                    const id = parseInt(parts[3]);
                    switchTab('products-view');
                    setTimeout(() => {
                        if (window.adminProducts && window.adminProducts.length > 0) {
                            if (window.openEditProductPage) window.openEditProductPage(id);
                        } else if (window.fetchProducts) {
                            window.fetchProducts().then(() => {
                                if (window.openEditProductPage) window.openEditProductPage(id);
                            });
                        }
                    }, 200);
                    return;
                }
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
                    document.querySelectorAll('.edit-perm-cb').forEach(cb => {
                        const mod = cb.dataset.module;
                        const action = cb.dataset.action;
                        if (mod && window.hasPermission(mod, action)) {
                            cb.checked = true;
                        }
                    });
                    switchTab(tabId);
                    return;
                }
                const [mod, action] = moduleMap[tabId] || [];
                if (mod && window.hasPermission(mod, action)) {
                    switchTab(tabId);
                    return;
                }
            }
        }

        // Listen for browser back/forward
        window.addEventListener('popstate', () => {
            routeFromPath();
        });


        // ============================================================================

