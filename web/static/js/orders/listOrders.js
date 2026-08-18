// ============================================================================
// listOrders.js - Orders Management
// ============================================================================

window.adminOrders = [];
window.filteredOrders = [];
window.currentOrdersPage = 1;
window.ordersPerPage = 10;

window.fetchOrders = async function() {
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    const tbody = document.getElementById('orders-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading orders...</td></tr>';
    
    try {
        const response = await fetch(API_ENDPOINTS.ORDERS, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log("Order Response:", response);
        if (!response.ok) throw new Error('Failed to fetch orders');
        
        const data = await response.json();
        console.log("Orders Data:", data);
        
        window.adminOrders = data;
        window.filterOrdersData();
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--accent-danger); padding: 20px;">${err.message}</td></tr>`;
    }
}

window.filterOrdersData = function() {
    const query = document.getElementById('search-orders-input')?.value.toLowerCase() || '';
    if (!query) {
        window.filteredOrders = [...window.adminOrders];
    } else {
        window.filteredOrders = window.adminOrders.filter(o => {
            return (o.id && String(o.id).toLowerCase().includes(query)) ||
                   (o.customer_name && String(o.customer_name).toLowerCase().includes(query)) ||
                   (o.customer_phone && String(o.customer_phone).toLowerCase().includes(query)) ||
                   (o.product_name && String(o.product_name).toLowerCase().includes(query));
        });
    }
    window.currentOrdersPage = 1;
    window.renderOrdersTable();
};

window.renderOrdersTable = function() {
    const tbody = document.getElementById('orders-table-body');
    if (!tbody) return;
    
    if (window.filteredOrders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No orders found</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    const totalPages = Math.ceil(window.filteredOrders.length / window.ordersPerPage) || 1;
    if (window.currentOrdersPage > totalPages) window.currentOrdersPage = totalPages;
    if (window.currentOrdersPage < 1) window.currentOrdersPage = 1;
    
    const startIndex = (window.currentOrdersPage - 1) * window.ordersPerPage;
    const endIndex = Math.min(startIndex + window.ordersPerPage, window.filteredOrders.length);
    
    const pageData = window.filteredOrders.slice(startIndex, endIndex);
    
    pageData.forEach((o, index) => {
        const serialNum = window.filteredOrders.length - (startIndex + index);
        const tr = document.createElement('tr');
        
        let statusBadge = '';
        if (o.status === 'PENDING' || o.status === 0) {
            statusBadge = `<span class="badge" style="background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(217,119,6,0.1)); color: #d97706; border: 1px solid rgba(245,158,11,0.2); font-weight: 700; font-size: 9px; padding: 2px 6px;"><i class="fa-solid fa-clock" style="margin-right: 3px; opacity: 0.8;"></i> Pending</span>`;
        } else if (o.status === 'APPROVED' || o.status === 1) {
            statusBadge = `<span class="badge" style="background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(37,99,235,0.1)); color: #2563eb; border: 1px solid rgba(59,130,246,0.2); font-weight: 700; font-size: 9px; padding: 2px 6px;"><i class="fa-solid fa-spinner fa-spin" style="margin-right: 3px; opacity: 0.8;"></i> Processing</span>`;
        } else {
            statusBadge = `<span class="badge" style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(5,150,105,0.1)); color: #059669; border: 1px solid rgba(16,185,129,0.2); font-weight: 700; font-size: 9px; padding: 2px 6px;"><i class="fa-solid fa-check-circle" style="margin-right: 3px; opacity: 0.8;"></i> Delivered</span>`;
        }

        tr.innerHTML = `
            <td style="font-weight: 700; color: #475569; font-size: 12px; width: 40px; text-align: center;">${serialNum}</td>
            <td>
                <span style="font-family: monospace; font-weight: 700; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 8px; border-radius: 6px; font-size: 11px;">${o.order_number || ('#ORD-' + String(o.id).padStart(4, '0'))}</span>
            </td>
            <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #8b5cf6, #6366f1); color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; box-shadow: 0 4px 10px rgba(99,102,241,0.2);">
                        ${(o.customer_name || 'C').substring(0,2).toUpperCase()}
                    </div>
                    <div>
                        <div style="font-weight: 700; color: var(--text-primary); font-size: 12px; letter-spacing: -0.2px;">${o.customer_name || 'N/A'}</div>
                        <div style="font-size: 11px; color: var(--text-muted); font-weight: 500; margin-top: 2px;"><i class="fa-solid fa-phone" style="font-size: 10px; margin-right: 4px; opacity: 0.7;"></i> ${o.customer_phone || '-'}</div>
                    </div>
                </div>
            </td>
            <td>
                <div style="font-weight: 600; color: #334155; font-size: 11px;">${o.product_name || '-'}</div>
                <div style="font-size: 10px; color: #64748b; font-weight: 600; margin-top: 2px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; display: inline-block;">Qty: ${o.quantity || 1}</div>
            </td>
            <td>
                <div style="font-weight: 800; color: #059669; font-size: 12px;">₹${(o.final_amount || 0).toFixed(2)}</div>
                <div style="font-size: 10px; color: #94a3b8; font-weight: 600; margin-top: 2px;">Total MRP: ₹${(o.mrp_amount || o.total_amount || 0).toFixed(2)}</div>
            </td>
            <td>
                <div style="color: #475569; font-size: 11px; font-weight: 600;"><i class="fa-regular fa-calendar" style="margin-right: 4px; color: #94a3b8;"></i> ${new Date(o.order_date).toLocaleDateString('en-IN', {day:'2-digit', month:'short', year:'numeric'})}</div>
                <div style="color: #94a3b8; font-size: 10px; font-weight: 500; margin-top: 2px;"><i class="fa-regular fa-clock" style="margin-right: 4px; opacity: 0.7;"></i> ${new Date(o.order_date).toLocaleTimeString('en-IN', {hour:'2-digit', minute:'2-digit'})}</div>
            </td>
            <td>${statusBadge}</td>
            <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">
                ${hasPermission('orders', 'view') ? `<button class="btn-action" title="View Order" onclick="openViewOrderPage(${o.id})" style="color: #3b82f6; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2);"><i class="fa-solid fa-eye"></i></button>` : ''}
                ${hasPermission('orders', 'edit') ? `<button class="btn-action" title="Edit Order Status" onclick="openEditOrderPage(${o.id})" style="color: #f59e0b; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2);"><i class="fa-solid fa-pen-to-square"></i></button>` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    window.renderOrdersPagination(totalPages);
};

window.renderOrdersPagination = function(totalPages) {
    const paginationContainer = document.getElementById('orders-pagination');
    if (!paginationContainer) return;
    
    let html = `<div class="pagination" style="display: flex; gap: 8px; justify-content: flex-end; padding: 12px 32px; border-top: 1px solid var(--border-glass);">`;
    html += `<button onclick="window.changeOrdersPage(${window.currentOrdersPage - 1})" ${window.currentOrdersPage === 1 ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentOrdersPage === 1 ? '#f1f5f9' : 'white'}; cursor: ${window.currentOrdersPage === 1 ? 'not-allowed' : 'pointer'};">Prev</button>`;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= window.currentOrdersPage - 1 && i <= window.currentOrdersPage + 1)) {
            html += `<button onclick="window.changeOrdersPage(${i})" style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${i === window.currentOrdersPage ? 'var(--accent-primary)' : 'white'}; color: ${i === window.currentOrdersPage ? 'white' : 'var(--text-primary)'}; cursor: pointer; border-color: ${i === window.currentOrdersPage ? 'var(--accent-primary)' : 'var(--border-glass)'};">${i}</button>`;
        } else if (i === window.currentOrdersPage - 2 || i === window.currentOrdersPage + 2) {
            html += `<span style="padding: 6px 4px;">...</span>`;
        }
    }
    
    html += `<button onclick="window.changeOrdersPage(${window.currentOrdersPage + 1})" ${window.currentOrdersPage === totalPages ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentOrdersPage === totalPages ? '#f1f5f9' : 'white'}; cursor: ${window.currentOrdersPage === totalPages ? 'not-allowed' : 'pointer'};">Next</button>`;
    html += `</div>`;
    paginationContainer.innerHTML = html;
};

window.changeOrdersPage = function(page) {
    window.currentOrdersPage = page;
    window.renderOrdersTable();
};
