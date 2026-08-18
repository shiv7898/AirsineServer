// ============================================================================
// viewQuery.js - Handles Full Page View of a Support Query
// ============================================================================

window.openViewQueryPage = function (queryId) {
  if (!window.queriesDataCache) {
    if (window.fetchQueries) {
      if (typeof toggleLoader === 'function') toggleLoader(true);
      window.fetchQueries().then(() => {
        if (typeof toggleLoader === 'function') toggleLoader(false);
        window.openViewQueryPage(queryId);
      });
    }
    return;
  }

  const q = window.queriesDataCache.find((x) => x.id === queryId);
  if (!q) {
    showToast("Query not found", "error");
    switchTab("queries-view");
    return;
  }

  // Update URL state
  history.pushState(null, "", `/queries/view/${queryId}`);

  const container = document.getElementById("view-query-container");
  const isResolved = q.status === "resolved";
  
  const statusBadge = isResolved
    ? '<span class="badge" style="background: rgba(34,197,94,0.1); color: var(--accent-success); font-size: 14px; padding: 6px 12px;"><i class="fa-solid fa-check"></i> Resolved</span>'
    : '<span class="badge" style="background: rgba(239,68,68,0.1); color: var(--accent-danger); font-size: 14px; padding: 6px 12px;"><i class="fa-solid fa-clock"></i> Pending</span>';

  // Format Dates
  const createdDate = new Date(q.created_at).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
  let resolvedDateHTML = "";
  if (isResolved && q.resolved_at) {
      const rDate = new Date(q.resolved_at).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
      resolvedDateHTML = `
        <div style="font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase;">Resolved At</div>
        <div style="font-size: 14px; font-weight: 500; color: #334155; margin-top: 4px;">${rDate}</div>
      `;
  }

  // Handle Images
  let imagesHTML = "";
  if (q.image) {
    const images = q.image.split(",");
    imagesHTML = `
      <div style="margin-top: 24px;">
        <h4 style="margin: 0 0 12px 0; font-size: 14px; color: #334155;"><i class="fa-solid fa-paperclip"></i> Attachments</h4>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
    `;
    images.forEach((img) => {
      imagesHTML += `
        <div style="width: 100px; height: 100px; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-glass); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;" 
             onclick="viewQueryImage('${q.image}')"
             onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='var(--shadow-md)'" 
             onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none'">
            <img src="/uploads/support/${img}" style="width: 100%; height: 100%; object-fit: cover;" />
        </div>
      `;
    });
    imagesHTML += `</div></div>`;
  }

  const html = `
    <div style="padding: 24px; padding-bottom: 100px; max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
      
      <!-- Left Column: Query Content -->
      <div style="display: flex; flex-direction: column; gap: 24px;">
        
        <div class="dashboard-panel" style="padding: 32px; display: flex; flex-direction: column; gap: 24px; background: linear-gradient(to bottom right, #ffffff, #f8fafc); border: 1px solid rgba(226, 232, 240, 0.8); box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-glass); padding-bottom: 20px;">
                <div>
                    <div style="font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; letter-spacing: 1px; color: var(--accent-primary); font-size: 13px; font-weight: 700; margin-bottom: 6px;">TICKET #${q.id}</div>
                    <div style="font-size: 24px; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">${q.query_type}</div>
                </div>
                <div style="transform: scale(1.1);">${statusBadge}</div>
            </div>

            <div style="display: flex; gap: 48px; padding: 16px; background: #f8fafc; border-radius: 12px; border: 1px dashed #cbd5e1;">
                <div>
                    <div style="font-size: 11px; color: #64748b; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;"><i class="fa-regular fa-calendar" style="margin-right: 4px;"></i> Submitted On</div>
                    <div style="font-size: 15px; font-weight: 600; color: #1e293b; margin-top: 6px;">${createdDate}</div>
                </div>
                ${resolvedDateHTML}
            </div>

            <div>
                <h4 style="margin: 0 0 12px 0; font-size: 15px; font-weight: 700; color: #1e293b; display: flex; align-items: center; gap: 8px;"><i class="fa-solid fa-align-left text-muted"></i> Message Description</h4>
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; font-size: 15px; color: #334155; white-space: pre-wrap; line-height: 1.7; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">${q.message}</div>
            </div>

            ${imagesHTML}
        </div>

        ${isResolved && q.resolution_message ? `
        <div class="dashboard-panel" style="padding: 32px; background: linear-gradient(135deg, rgba(34,197,94,0.05) 0%, rgba(34,197,94,0.1) 100%); border: 1px solid rgba(34,197,94,0.3); box-shadow: 0 4px 15px rgba(34, 197, 94, 0.05);">
            <h4 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 700; color: #166534; display: flex; align-items: center; gap: 10px;"><div style="background: #22c55e; color: white; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 50%;"><i class="fa-solid fa-check"></i></div> Resolution Provided</h4>
            <div style="font-size: 15px; color: #14532d; white-space: pre-wrap; line-height: 1.7; background: white; padding: 20px; border-radius: 12px; border: 1px solid rgba(34,197,94,0.2);">${q.resolution_message}</div>
        </div>
        ` : ''}

      </div>

      <!-- Right Column: User & Action -->
      <div style="display: flex; flex-direction: column; gap: 24px;">
        
        <div class="dashboard-panel" style="padding: 24px; border-top: 4px solid var(--accent-primary);">
            <h3 style="margin: 0 0 20px 0; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #64748b; border-bottom: 1px solid var(--border-glass); padding-bottom: 12px;">User Information</h3>
            
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="width: 56px; height: 56px; border-radius: 16px; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); color: #2563eb; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 800; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.1);">
                    ${q.user_name.charAt(0).toUpperCase()}
                </div>
                <div>
                    <div style="font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 2px;">${q.user_name}</div>
                    <div style="font-size: 13px; color: #64748b; font-weight: 500;">${q.user_email}</div>
                </div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; background: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0;">
                <span style="font-size: 13px; color: #64748b; font-weight: 700; text-transform: uppercase;">Role</span>
                <span class="badge" style="background: white; border: 1px solid #cbd5e1; color: #334155; font-weight: 700; padding: 6px 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">${q.user_role}</span>
            </div>
        </div>

      </div>

    </div>
  `;

  container.innerHTML = html;
  switchTab("view-query-view");
};


