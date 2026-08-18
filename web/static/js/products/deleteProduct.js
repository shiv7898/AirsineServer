window.deleteProduct = async function(id) {
    if (!confirm('Are you sure you want to delete this product?')) return;
    const token = localStorage.getItem('admin_token');
    if (!token) return window.showToast('Session expired, please login again.', 'error');
    
    try {
        const response = await fetch(window.API_ENDPOINTS.PRODUCT_DETAIL(id), {
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
        
        window.showToast('Product deleted successfully', 'success');
        window.fetchProducts(); // Refresh the table
    } catch (err) {
        window.showToast(err.message, 'error');
    }
};
