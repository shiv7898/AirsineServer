// ============================================================================
// STAFF LISTING & TABLE MANAGEMENT
// ============================================================================

window.renderStaffTable = function() {
    const tbodyStaff = document.getElementById('admin-staff-table-body');
    if (!tbodyStaff) return;
    tbodyStaff.innerHTML = '';
    
    const totalPages = Math.ceil(window.filteredStaff.length / window.staffPerPage) || 1;
    if (window.currentStaffPage > totalPages) window.currentStaffPage = totalPages;
    if (window.currentStaffPage < 1) window.currentStaffPage = 1;
    
    const startIndex = (window.currentStaffPage - 1) * window.staffPerPage;
    const endIndex = Math.min(startIndex + window.staffPerPage, window.filteredStaff.length);
    
    const pageData = window.filteredStaff.slice(startIndex, endIndex);
    
    pageData.forEach((user, index) => {
        const row = document.createElement('tr');
        const srNo = window.filteredStaff.length - (startIndex + index);
        
        let roleColor = user.role === 'admin' ? '#8b5cf6' : '#ec4899';
        let roleBg = user.role === 'admin' ? 'rgba(139,92,246,0.1)' : 'rgba(236,72,153,0.1)';
        let roleBorder = user.role === 'admin' ? 'rgba(139,92,246,0.2)' : 'rgba(236,72,153,0.2)';
        let roleIcon = user.role === 'admin' ? 'fa-user-shield' : 'fa-user-tie';
        let roleHtml = `<span class="badge" style="background: ${roleBg}; color: ${roleColor}; border: 1px solid ${roleBorder}; font-weight: 700; text-transform: capitalize;"><i class="fa-solid ${roleIcon}" style="margin-right: 4px; opacity: 0.8;"></i>${(user.role || 'Staff').replace('_', ' ')}</span>`;

        row.innerHTML = `
            <td style="font-weight: 700; color: #94a3b8;">${srNo}.</td>
            <td>
                <span style="font-family: monospace; font-weight: 700; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 8px; border-radius: 6px; font-size: 11px;">${user.custom_id || user.id}</span>
            </td>
            <td>${window.getAvatarHtml(user)}</td>
            <td style="color: #64748b; font-weight: 500; font-size: 11px;">${user.email}</td>
            <td>${roleHtml}</td>
            <td style="color: #475569; font-weight: 600; font-size: 11px;">${user.phone || '-'}</td>
            <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">${window.getActionsHtml(user)}</td>
        `;
        tbodyStaff.appendChild(row);
    });
    
    window.renderStaffPagination(totalPages);
};

window.renderStaffPagination = function(totalPages) {
    const paginationContainer = document.getElementById('staff-pagination');
    if (!paginationContainer) return;
    
    let html = `<div class="pagination" style="display: flex; gap: 8px; justify-content: flex-end; padding: 12px 32px; border-top: 1px solid var(--border-glass);">`;
    html += `<button onclick="window.changeStaffPage(${window.currentStaffPage - 1})" ${window.currentStaffPage === 1 ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentStaffPage === 1 ? '#f1f5f9' : 'white'}; cursor: ${window.currentStaffPage === 1 ? 'not-allowed' : 'pointer'};">Prev</button>`;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= window.currentStaffPage - 1 && i <= window.currentStaffPage + 1)) {
            html += `<button onclick="window.changeStaffPage(${i})" style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${i === window.currentStaffPage ? 'var(--accent-primary)' : 'white'}; color: ${i === window.currentStaffPage ? 'white' : 'var(--text-primary)'}; cursor: pointer; border-color: ${i === window.currentStaffPage ? 'var(--accent-primary)' : 'var(--border-glass)'};">${i}</button>`;
        } else if (i === window.currentStaffPage - 2 || i === window.currentStaffPage + 2) {
            html += `<span style="padding: 6px 4px;">...</span>`;
        }
    }
    
    html += `<button onclick="window.changeStaffPage(${window.currentStaffPage + 1})" ${window.currentStaffPage === totalPages ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentStaffPage === totalPages ? '#f1f5f9' : 'white'}; cursor: ${window.currentStaffPage === totalPages ? 'not-allowed' : 'pointer'};">Next</button>`;
    html += `</div>`;
    paginationContainer.innerHTML = html;
};

window.changeStaffPage = function(page) {
    window.currentStaffPage = page;
    window.renderStaffTable();
};

window.filterStaffData = function(query) {
    const lowerQuery = query.toLowerCase().trim();
    if (!lowerQuery) {
        window.filteredStaff = [...window.allStaff];
    } else {
        window.filteredStaff = window.allStaff.filter(user => {
            return (user.name && user.name.toLowerCase().includes(lowerQuery)) ||
                   (user.email && user.email.toLowerCase().includes(lowerQuery)) ||
                   (user.custom_id && user.custom_id.toString().toLowerCase().includes(lowerQuery)) ||
                   (user.phone && String(user.phone).toLowerCase().includes(lowerQuery));
        });
    }
    window.currentStaffPage = 1;
    window.renderStaffTable();
};
