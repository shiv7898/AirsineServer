// ============================================================================
// listQueries.js - Queries & Support Management
// ============================================================================

async function fetchQueries() {
    const token = localStorage.getItem('admin_token');
    if (!token) return;

    const tbody = document.getElementById('queries-table-body');
    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading queries...</td></tr>';
    
    try {
        const response = await fetch(API_ENDPOINTS.QUERIES, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Failed to fetch queries');
        
        const data = await response.json();
        console.log("Queries Data:", data);
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No queries found</td></tr>';
            return;
        }
        
        window.queriesDataCache = data; // Cache data for the modal

        tbody.innerHTML = '';
        data.forEach(q => {
            const tr = document.createElement('tr');
            
            const isResolved = q.status === 'resolved';
            const statusBadge = isResolved 
                ? '<span class="badge" style="background: rgba(34,197,94,0.1); color: var(--accent-success);">Resolved</span>' 
                : '<span class="badge" style="background: rgba(239,68,68,0.1); color: var(--accent-danger);">Pending</span>';

            const viewBtn = `<div class="btn-action" title="View Details" onclick="viewQueryDetails(${q.id})" style="color: var(--accent-primary); background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2);"><i class="fa-solid fa-eye"></i></div>`;
            const editBtn = isResolved ? '' : `<div class="btn-action" title="Resolve Query" onclick="editQueryDetails(${q.id})" style="color: var(--accent-success); background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.2);"><i class="fa-solid fa-pen"></i></div>`;

            let imageThumbnail = `<span style="color: var(--text-muted); font-size: 11px; font-style: italic;">None</span>`;
            
            if (q.image) {
                const imagesArray = q.image.split(',');
                const firstImage = imagesArray[0];
                const countBadge = imagesArray.length > 1 
                    ? `<div style="position: absolute; top: -5px; right: -5px; background: var(--accent-primary); color: white; border-radius: 50%; width: 20px; height: 20px; font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">+${imagesArray.length - 1}</div>` 
                    : '';
                
                imageThumbnail = `<div style="position: relative; width: 44px; height: 44px; margin: 0 auto; cursor: pointer;" onclick="viewQueryImage('${q.image}')" title="Click to view ${imagesArray.length} image(s)">
                    <div style="width: 100%; height: 100%; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-glass); box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='scale(1.15)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.05)'">
                        <img src="/uploads/support/${firstImage}" style="width: 100%; height: 100%; object-fit: cover;" />
                    </div>
                    ${countBadge}
                </div>`;
            }

            tr.innerHTML = `
                <td><span style="font-family: monospace; font-weight: 700; color: #64748b; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 8px; border-radius: 6px; font-size: 11px;">#${q.id}</span></td>
                <td style="font-weight: 700; font-size: 12px; color: var(--text-primary);">${q.user_name}<br><span style="font-size:11px; font-weight: 500; color: var(--text-muted);">${q.user_email}</span></td>
                <td><span class="badge">${q.user_role}</span></td>
                <td style="font-size: 11px;">${q.query_type}</td>
                <td style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 11px;" title="${q.message}">${q.message}</td>
                <td style="text-align: center;">${imageThumbnail}</td>
                <td>${statusBadge}</td>
                <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">
                    ${viewBtn}
                    ${editBtn}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--accent-danger); padding: 20px;">${err.message}</td></tr>`;
    }
}

window.viewQueryDetails = function(queryId) {
    console.log("Opening full page view for query:", queryId);
    if (window.openViewQueryPage) {
        window.openViewQueryPage(queryId);
    } else {
        console.error("openViewQueryPage is not defined");
    }
};

window.editQueryDetails = function(queryId) {
    console.log("Opening full page edit for query:", queryId);
    if (window.openEditQueryPage) {
        window.openEditQueryPage(queryId);
    } else {
        console.error("openEditQueryPage is not defined");
    }
};
