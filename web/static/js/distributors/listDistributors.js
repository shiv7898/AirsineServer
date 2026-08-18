// ============================================================================
// DISTRIBUTORS LISTING & TABLE MANAGEMENT
// ============================================================================

window.renderDistributorsTable = function() {
    const tbodyDistributors = document.getElementById('distributors-table-body');
    if (!tbodyDistributors) return;
    tbodyDistributors.innerHTML = '';
    
    const totalPages = Math.ceil(window.filteredDistributors.length / window.distributorsPerPage) || 1;
    if (window.currentDistributorsPage > totalPages) window.currentDistributorsPage = totalPages;
    if (window.currentDistributorsPage < 1) window.currentDistributorsPage = 1;
    
    const startIndex = (window.currentDistributorsPage - 1) * window.distributorsPerPage;
    const endIndex = Math.min(startIndex + window.distributorsPerPage, window.filteredDistributors.length);
    
    const pageData = window.filteredDistributors.slice(startIndex, endIndex);
    
    pageData.forEach((user, index) => {
        const row = document.createElement('tr');
        const srNo = window.filteredDistributors.length - (startIndex + index);
        
        let roleColor = '#0ea5e9';
        let roleBg = 'rgba(14,165,233,0.1)';
        let roleBorder = 'rgba(14,165,233,0.2)';
        let roleIcon = 'fa-building';
        let roleHtml = `<span class="badge" style="background: ${roleBg}; color: ${roleColor}; border: 1px solid ${roleBorder}; font-weight: 700; text-transform: capitalize;"><i class="fa-solid ${roleIcon}" style="margin-right: 4px; opacity: 0.8;"></i>${(user.role || 'Distributor').replace('_', ' ')}</span>`;

        row.innerHTML = `
            <td style="font-weight: 700; color: #94a3b8;">${srNo}</td>
            <td>
                <span style="font-family: monospace; font-weight: 700; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 8px; border-radius: 6px; font-size: 11px;">${user.custom_id || user.id}</span>
            </td>
            <td style="font-weight: 600; color: #334155; font-size: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <i class="fa-regular fa-building" style="color: #94a3b8; font-size: 12px;"></i>
                    ${user.companyName || '-'}
                </div>
            </td>
            <td>${window.getAvatarHtml(user)}</td>
            <td>${roleHtml}</td>
            <td style="color: #64748b; font-weight: 500; font-size: 11px;">${user.email}</td>
            <td style="color: #475569; font-weight: 600; font-size: 11px;">${user.phone || '-'}</td>
            <td>
                <span style="display: inline-flex; align-items: center; gap: 4px; background: rgba(16,185,129,0.1); color: #059669; border: 1px solid rgba(16,185,129,0.2); padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 13px;">
                    <i class="fa-solid fa-percent" style="font-size: 10px;"></i>
                    ${user.commission !== undefined ? user.commission : '0'}
                </span>
            </td>
            <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">${window.getActionsHtml(user)}</td>
        `;
        tbodyDistributors.appendChild(row);
    });
    
    window.renderDistributorsPagination(totalPages);
};

window.renderDistributorsPagination = function(totalPages) {
    const paginationContainer = document.getElementById('distributors-pagination');
    if (!paginationContainer) return;
    
    let html = `<div class="pagination" style="display: flex; gap: 8px; justify-content: flex-end; padding: 12px 32px; border-top: 1px solid var(--border-glass);">`;
    html += `<button onclick="window.changeDistributorsPage(${window.currentDistributorsPage - 1})" ${window.currentDistributorsPage === 1 ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentDistributorsPage === 1 ? '#f1f5f9' : 'white'}; cursor: ${window.currentDistributorsPage === 1 ? 'not-allowed' : 'pointer'};">Prev</button>`;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= window.currentDistributorsPage - 1 && i <= window.currentDistributorsPage + 1)) {
            html += `<button onclick="window.changeDistributorsPage(${i})" style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${i === window.currentDistributorsPage ? 'var(--accent-primary)' : 'white'}; color: ${i === window.currentDistributorsPage ? 'white' : 'var(--text-primary)'}; cursor: pointer; border-color: ${i === window.currentDistributorsPage ? 'var(--accent-primary)' : 'var(--border-glass)'};">${i}</button>`;
        } else if (i === window.currentDistributorsPage - 2 || i === window.currentDistributorsPage + 2) {
            html += `<span style="padding: 6px 4px;">...</span>`;
        }
    }
    
    html += `<button onclick="window.changeDistributorsPage(${window.currentDistributorsPage + 1})" ${window.currentDistributorsPage === totalPages ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentDistributorsPage === totalPages ? '#f1f5f9' : 'white'}; cursor: ${window.currentDistributorsPage === totalPages ? 'not-allowed' : 'pointer'};">Next</button>`;
    html += `</div>`;
    paginationContainer.innerHTML = html;
};

window.changeDistributorsPage = function(page) {
    window.currentDistributorsPage = page;
    window.renderDistributorsTable();
};

window.filterDistributorsData = function(query) {
    const lowerQuery = query.toLowerCase().trim();
    if (!lowerQuery) {
        window.filteredDistributors = [...window.allDistributors];
    } else {
        window.filteredDistributors = window.allDistributors.filter(user => {
            return (user.companyName && user.companyName.toLowerCase().includes(lowerQuery)) ||
                   (user.name && user.name.toLowerCase().includes(lowerQuery)) ||
                   (user.email && user.email.toLowerCase().includes(lowerQuery)) ||
                   (user.custom_id && user.custom_id.toString().toLowerCase().includes(lowerQuery)) ||
                   (user.phone && String(user.phone).toLowerCase().includes(lowerQuery));
        });
    }
    window.currentDistributorsPage = 1;
    window.renderDistributorsTable();
};
