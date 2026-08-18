// ==========================================
// apiConfig.js - Centralized API Endpoints
// ==========================================

const API_ENDPOINTS = {
    // Authentication
    LOGIN: '/api/v1/web/user/login',
    
    // Dashboard
    DASHBOARD: '/api/v1/web/admin/dashboard',
    
    // Users & Staff
    USERS: '/api/v1/web/admin/users',
    CREATE_STAFF: '/api/v1/web/admin/create-staff',
    USER_DETAIL: (userId, role) => role ? `/api/v1/web/admin/users/${userId}/view?role=${role}` : `/api/v1/web/admin/users/${userId}/view`,
    EDIT_USER_DATA: (userId, role) => role ? `/api/v1/web/admin/users/${userId}/edit?role=${role}` : `/api/v1/web/admin/users/${userId}/edit`,
    UPDATE_USER: (userId, role) => role ? `/api/v1/web/admin/users/${userId}?role=${role}` : `/api/v1/web/admin/users/${userId}`,
    
    // Orders
    ORDERS: '/api/v1/web/admin/orders',
    
    // Support Queries
    QUERIES: '/api/v1/web/support/admin/queries',
    RESOLVE_QUERY: (queryId) => `/api/v1/web/support/admin/queries/${queryId}/resolve`,
    
    // Products
    PRODUCTS: '/api/v1/web/admin/products',
    PRODUCT_DETAIL: (id) => `/api/v1/web/products/${id}`,
    ADD_PRODUCT: (target) => target === 'distributor' ? '/api/v1/mobile/distributor/add-product' : '/api/v1/web/products/add-product',
    UPDATE_PRODUCT: (target, productId) => target === 'distributor' ? `/api/v1/mobile/distributor/update-product/${productId}` : `/api/v1/web/products/update-product/${productId}`
};

// Make sure it's globally available for browser environments
if (typeof window !== 'undefined') {
    window.API_ENDPOINTS = API_ENDPOINTS;
}
