window.openViewProductPage = function(productId) {
    const product = window.adminProducts.find(p => p.id === productId);
    if (!product) {
        window.showToast('Product not found in data.', 'error');
        return;
    }
    
    const container = document.getElementById('view-product-container');

    // Update URL
    history.pushState(null, '', '/products/view/' + productId);

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
    window.switchTab('view-product-view');
};
