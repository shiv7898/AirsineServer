// ============================================================================
// PATIENTS & DOCTORS LISTING & TABLE MANAGEMENT
// ============================================================================

window.renderUsersTable = function() {
    const tbodyUsers = document.getElementById('users-table-body');
    if (!tbodyUsers) return;
    tbodyUsers.innerHTML = '';
    
    const totalPages = Math.ceil(window.filteredPatientsDoctors.length / window.usersPerPage) || 1;
    if (window.currentUsersPage > totalPages) window.currentUsersPage = totalPages;
    if (window.currentUsersPage < 1) window.currentUsersPage = 1;
    
    const startIndex = (window.currentUsersPage - 1) * window.usersPerPage;
    const endIndex = Math.min(startIndex + window.usersPerPage, window.filteredPatientsDoctors.length);
    
    const pageData = window.filteredPatientsDoctors.slice(startIndex, endIndex);
    
    pageData.forEach((user, index) => {
        const row = document.createElement('tr');
        const srNo = window.filteredPatientsDoctors.length - (startIndex + index);
        
        let roleColor = user.role === 'doctor' ? '#3b82f6' : '#10b981';
        let roleBg = user.role === 'doctor' ? 'rgba(59,130,246,0.1)' : 'rgba(16,185,129,0.1)';
        let roleBorder = user.role === 'doctor' ? 'rgba(59,130,246,0.2)' : 'rgba(16,185,129,0.2)';
        let roleIcon = user.role === 'doctor' ? 'fa-user-doctor' : 'fa-user-injured';
        
        let roleHtml = `<span class="badge" style="background: ${roleBg}; color: ${roleColor}; border: 1px solid ${roleBorder}; font-weight: 700; text-transform: capitalize;"><i class="fa-solid ${roleIcon}" style="margin-right: 4px; opacity: 0.8;"></i>${(user.role || 'Patient').replace('_', ' ')}</span>`;

        row.innerHTML = `
            <td style="font-weight: 700; color: #94a3b8;">${srNo}.</td>
            <td>
                <span style="font-family: monospace; font-weight: 700; color: #64748b; border: 1px solid #e2e8f0; background: #f8fafc; padding: 4px 8px; border-radius: 6px; font-size: 11px;">${user.custom_id || user.id}</span>
            </td>
            <td>${window.getAvatarHtml(user)}</td>
            <td style="color: #64748b; font-weight: 500; font-size: 11px;">${user.email}</td>
            <td>${roleHtml}</td>
            <td style="color: #475569; font-weight: 600; font-size: 11px;">${user.phone || '-'}</td>
            <td>
                <div style="font-weight: 600; color: #475569; font-size: 11 px;">${user.gender || '-'}</div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 500;">${user.age ? user.age + ' yrs' : '-'}</div>
            </td>
            <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">${window.getActionsHtml(user)}</td>
        `;
        tbodyUsers.appendChild(row);
    });
    
    window.renderUsersPagination(totalPages);
};

window.renderUsersPagination = function(totalPages) {
    const paginationContainer = document.getElementById('users-pagination');
    if (!paginationContainer) return;
    
    let html = `<div class="pagination" style="display: flex; gap: 8px; justify-content: flex-end; padding: 12px 32px; border-top: 1px solid var(--border-glass);">`;
    
    html += `<button onclick="window.changeUsersPage(${window.currentUsersPage - 1})" ${window.currentUsersPage === 1 ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentUsersPage === 1 ? '#f1f5f9' : 'white'}; cursor: ${window.currentUsersPage === 1 ? 'not-allowed' : 'pointer'};">Prev</button>`;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= window.currentUsersPage - 1 && i <= window.currentUsersPage + 1)) {
            html += `<button onclick="window.changeUsersPage(${i})" style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${i === window.currentUsersPage ? 'var(--accent-primary)' : 'white'}; color: ${i === window.currentUsersPage ? 'white' : 'var(--text-primary)'}; cursor: pointer; border-color: ${i === window.currentUsersPage ? 'var(--accent-primary)' : 'var(--border-glass)'};">${i}</button>`;
        } else if (i === window.currentUsersPage - 2 || i === window.currentUsersPage + 2) {
            html += `<span style="padding: 6px 4px;">...</span>`;
        }
    }
    
    html += `<button onclick="window.changeUsersPage(${window.currentUsersPage + 1})" ${window.currentUsersPage === totalPages ? 'disabled' : ''} style="padding: 6px 12px; border: 1px solid var(--border-glass); border-radius: 8px; background: ${window.currentUsersPage === totalPages ? '#f1f5f9' : 'white'}; cursor: ${window.currentUsersPage === totalPages ? 'not-allowed' : 'pointer'};">Next</button>`;
    
    html += `</div>`;
    paginationContainer.innerHTML = html;
};

window.changeUsersPage = function(page) {
    window.currentUsersPage = page;
    window.renderUsersTable();
};

window.filterUsersData = function(query) {
    const lowerQuery = query.toLowerCase().trim();
    if (!lowerQuery) {
        window.filteredPatientsDoctors = [...window.allPatientsDoctors];
    } else {
        window.filteredPatientsDoctors = window.allPatientsDoctors.filter(user => {
            return (user.name && user.name.toLowerCase().includes(lowerQuery)) ||
                   (user.email && user.email.toLowerCase().includes(lowerQuery)) ||
                   (user.custom_id && user.custom_id.toString().toLowerCase().includes(lowerQuery)) ||
                   (user.phone && String(user.phone).toLowerCase().includes(lowerQuery));
        });
    }
    window.currentUsersPage = 1;
    window.renderUsersTable();
};
