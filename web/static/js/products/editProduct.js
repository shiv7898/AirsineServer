window.openEditProductPage = function(productId) {
    const product = window.adminProducts.find(p => p.id === productId);
    if (!product) {
        window.showToast('Product not found in data.', 'error');
        return;
    }
    
    // Update URL
    history.pushState(null, '', '/products/edit/' + productId);

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
    
    window.switchTab('edit-product-view');
};

window.submitEditProduct = async function(e) {
    if(e) e.preventDefault();
    const token = localStorage.getItem('admin_token');
    if (!token) return window.showToast('Session expired, please login again.', 'error');
    
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

    const endpoint = window.API_ENDPOINTS.UPDATE_PRODUCT(target, productId);

    window.toggleLoader(true);
    try {
        const response = await fetch(endpoint, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        if (response.ok) {
            window.showToast('Product updated successfully!', 'success');
            window.switchTab('products-view');
            window.fetchProducts();
        } else {
            const err = await response.json();
            window.showToast(err.detail || 'Failed to update product', 'error');
        }
    } catch (error) {
        console.error(error);
        window.showToast('Network error while updating product', 'error');
    } finally {
        window.toggleLoader(false);
    }
};
