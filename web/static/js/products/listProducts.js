window.adminProducts = [];
window.filteredProducts = [];
window.currentProductsPage = 1;
window.productsPerPage = 10;

window.fetchProducts = async function() {
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    const tbody = document.getElementById('products-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading products...</td></tr>';
    
    try {
        const response = await fetch(API_ENDPOINTS.PRODUCTS, {
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
        console.log("Product Data:", data);
        
        // Dynamically generate the AIR-TYPE-XXXX product code as fallback for old records
        data.forEach(p => {
            if (!p.product_code) {
                const type = p.product_type ? p.product_type.toUpperCase().replace(/\s+/g, '') : 'PROD';
                p.product_code = `AIR-${type}-${String(p.id).padStart(4, '0')}`;
            }
        });
        
        window.adminProducts = data;
        window.filterProductsData();
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--accent-danger); padding: 20px;">Error: ${err.message}</td></tr>`;
        showToast(err.message, 'error');
        console.error('[fetchProducts] error:', err.message);
    }
};

window.filterProductsData = function() {
    const query = document.getElementById('search-products-input')?.value.toLowerCase() || '';
    if (!query) {
        window.filteredProducts = [...window.adminProducts];
    } else {
        window.filteredProducts = window.adminProducts.filter(p => {
            return (p.product_code && String(p.product_code).toLowerCase().includes(query)) ||
                   (p.product_name && String(p.product_name).toLowerCase().includes(query)) ||
                   (p.product_type && String(p.product_type).toLowerCase().includes(query)) ||
                   (p.model_name && String(p.model_name).toLowerCase().includes(query)) ||
                   (p.brand && String(p.brand).toLowerCase().includes(query)) ||
                   (p.target_audience && String(p.target_audience).toLowerCase().includes(query));
        });
    }
    window.currentProductsPage = 1;
    window.renderProductsTable();
};

window.renderProductsTable = function() {
    const tbody = document.getElementById('products-table-body');
    if (!tbody) return;

    if (window.filteredProducts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 20px;">No products found</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    const totalPages = Math.ceil(window.filteredProducts.length / window.productsPerPage) || 1;
    if (window.currentProductsPage > totalPages) window.currentProductsPage = totalPages;
    if (window.currentProductsPage < 1) window.currentProductsPage = 1;
    
    const startIndex = (window.currentProductsPage - 1) * window.productsPerPage;
    const endIndex = Math.min(startIndex + window.productsPerPage, window.filteredProducts.length);
    
    const pageData = window.filteredProducts.slice(startIndex, endIndex);

    pageData.forEach((p, index) => {
        const serialNum = window.filteredProducts.length - (startIndex + index);
        let imageHtml = `<div style="width: 40px; height: 40px; border-radius: 10px; background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(14,165,233,0.1)); border: 1px solid rgba(59,130,246,0.2); display: flex; align-items: center; justify-content: center; color: #3b82f6; font-size: 18px; flex-shrink: 0;"><i class="fa-solid fa-box-open"></i></div>`;
        if (p.product_images) {
            let firstImg = '';
            try {
                let parsed = JSON.parse(p.product_images);
                if (Array.isArray(parsed) && parsed.length > 0) firstImg = parsed[0];
            } catch (e) {
                firstImg = p.product_images.split(',')[0].trim().replace(/['"\\[\\]]/g, '');
            }
            
            if (firstImg) {
                imageHtml = `<div style="width: 40px; height: 40px; border-radius: 10px; overflow: hidden; border: 1px solid rgba(0,0,0,0.1); flex-shrink: 0; background: #fff;"><img src="/uploads/products/${firstImg}" style="width: 100%; height: 100%; object-fit: contain;" onerror="this.outerHTML='<div style=\\'width:100%;height:100%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:16px;\\'><i class=\\'fa-solid fa-box-open\\'></i></div>'" /></div>`;
            }
        }
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight: 700; color: #475569; font-size: 12px; width: 40px; text-align: center;">${serialNum}</td>
            <td>
                <span style="font-family: monospace; font-weight: 700; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 8px; border-radius: 6px; font-size: 11px;">${p.product_code}</span>
            </td>
            <td>
                <div style="display: flex; align-items: center; gap: 12px;">
                    ${imageHtml}
                    <div>
                        <div style="font-weight: 700; color: var(--text-primary); font-size: 12px; letter-spacing: -0.2px;">${p.product_name}</div>
                        <div style="font-size: 11px; color: var(--text-muted); font-weight: 500; margin-top: 2px;">${p.product_type}</div>
                    </div>
                </div>
            </td>
            <td>
                <div style="font-weight: 600; color: #475569; font-size: 11px;">${p.brand || '-'}</div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 500; margin-top: 2px;">${p.model_name || '-'}</div>
            </td>
            <td>
                <div style="font-weight: 800; color: #059669; font-size: 12px;">₹${p.selling_price || p.unit_mrp}</div>
                <div style="font-size: 11px; color: #94a3b8; text-decoration: line-through; font-weight: 500; margin-top: 2px;">MRP ₹${p.unit_mrp}</div>
            </td>
            <td>
                <span class="badge" style="background: ${p.target_audience === 'distributor' ? 'linear-gradient(135deg, rgba(236,72,153,0.1), rgba(219,39,119,0.1))' : 'linear-gradient(135deg, rgba(139,92,246,0.1), rgba(109,40,217,0.1))'}; color: ${p.target_audience === 'distributor' ? '#db2777' : '#7c3aed'}; text-transform: capitalize; border: 1px solid ${p.target_audience === 'distributor' ? 'rgba(236,72,153,0.2)' : 'rgba(139,92,246,0.2)'}; font-weight: 700; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <i class="fa-solid ${p.target_audience === 'distributor' ? 'fa-building' : 'fa-users'}" style="margin-right: 4px; opacity: 0.8;"></i>
                    ${p.target_audience === 'patient_doctor' ? 'Patient & Doctor' : (p.target_audience || 'All')}
                </span>
            </td>
            <td>
                <span style="display: inline-block; background: ${p.stock_pieces > 10 ? 'rgba(16,185,129,0.1)' : (p.stock_pieces > 0 ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)')}; color: ${p.stock_pieces > 10 ? '#059669' : (p.stock_pieces > 0 ? '#d97706' : '#dc2626')}; border: 1px solid ${p.stock_pieces > 10 ? 'rgba(16,185,129,0.2)' : (p.stock_pieces > 0 ? 'rgba(245,158,11,0.2)' : 'rgba(239,68,68,0.2)')}; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 11px; text-align: center; min-width: 60px;">
                    ${p.stock_pieces} <span style="font-size: 9px; opacity: 0.8;">pcs</span>
                </span>
            </td>
            <td><span class="badge" style="background: ${p.product_status === 'Active' ? 'linear-gradient(135deg, rgba(34,197,94,0.1), rgba(21,128,61,0.1))' : 'linear-gradient(135deg, rgba(239,68,68,0.1), rgba(185,28,28,0.1))'}; color: ${p.product_status === 'Active' ? '#16a34a' : '#dc2626'}; border: 1px solid ${p.product_status === 'Active' ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)'}; font-weight: 700;">
                    <i class="fa-solid ${p.product_status === 'Active' ? 'fa-check-circle' : 'fa-times-circle'}" style="margin-right: 4px; opacity: 0.8;"></i>
                    ${p.product_status || (p.is_available ? 'Active' : 'Inactive')}
                </span>
            </td>
            <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">
                ${window.hasPermission('products', 'view') ? `<button class="btn-action" title="View Product" onclick="window.openViewProductPage(${p.id})" style="color: #3b82f6; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2);"><i class="fa-solid fa-eye"></i></button>` : ''}
                ${window.hasPermission('products', 'edit') ? `<button class="btn-action" title="Edit Product" onclick="window.openEditProductPage(${p.id})" style="color: #f59e0b; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2);"><i class="fa-solid fa-pen-to-square"></i></button>` : ''}
                ${window.hasPermission('products', 'delete') ? `<button class="btn-action" title="Delete Product" onclick="window.deleteProduct(${p.id})" style="color: #ef4444; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2);"><i class="fa-solid fa-trash-can"></i></button>` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    window.renderProductsPagination(totalPages);
};

window.renderProductsPagination = function(totalPages) {
    const paginationContainer = document.getElementById('products-pagination');
    if (!paginationContainer) return;
    
    let html = `<div class="pagination" style="display: flex; gap: 8px; justify-content: flex-end; padding: 12px 32px; border-top: 1px solid var(--border-glass);">`;
    html += `<button onclick="window.changeProductsPage(${window.currentProductsPage - 1})" ${window.currentProductsPage === 1 ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentProductsPage === 1 ? '#f1f5f9' : 'white'}; cursor: ${window.currentProductsPage === 1 ? 'not-allowed' : 'pointer'};">Prev</button>`;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= window.currentProductsPage - 1 && i <= window.currentProductsPage + 1)) {
            html += `<button onclick="window.changeProductsPage(${i})" style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${i === window.currentProductsPage ? 'var(--accent-primary)' : 'white'}; color: ${i === window.currentProductsPage ? 'white' : 'var(--text-primary)'}; cursor: pointer; border-color: ${i === window.currentProductsPage ? 'var(--accent-primary)' : 'var(--border-glass)'};">${i}</button>`;
        } else if (i === window.currentProductsPage - 2 || i === window.currentProductsPage + 2) {
            html += `<span style="padding: 6px 4px;">...</span>`;
        }
    }
    
    html += `<button onclick="window.changeProductsPage(${window.currentProductsPage + 1})" ${window.currentProductsPage === totalPages ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentProductsPage === totalPages ? '#f1f5f9' : 'white'}; cursor: ${window.currentProductsPage === totalPages ? 'not-allowed' : 'pointer'};">Next</button>`;
    html += `</div>`;
    
    paginationContainer.innerHTML = html;
};

window.changeProductsPage = function(page) {
    const totalPages = Math.ceil(window.filteredProducts.length / window.productsPerPage) || 1;
    if (page >= 1 && page <= totalPages) {
        window.currentProductsPage = page;
        window.renderProductsTable();
    }
};
