// Preview Product Modal Logic
window.openProductPreviewModal = function(e) {
    if(e) e.preventDefault();
    
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
};

// Submit Create Product (Called from Modal)
window.confirmAndSubmitProduct = async function() {
    const token = localStorage.getItem('admin_token');
    if (!token) return window.showToast('Session expired, please login again.', 'error');

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

    const endpoint = window.API_ENDPOINTS.ADD_PRODUCT(target);

    window.toggleLoader(true);
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        if (response.ok) {
            window.showToast('Product created successfully!');
            window.closeModal('product-preview-modal');
            
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
            
            window.switchTab('products-view');
        } else {
            const err = await response.json();
            window.showToast(err.detail || 'Failed to create product', 'error');
        }
    } catch (error) {
        console.error(error);
        window.showToast('Network error while creating product', 'error');
    } finally {
        window.toggleLoader(false);
    }
};
