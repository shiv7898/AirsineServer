// ============================================================================
// DELETE DISTRIBUTOR LOGIC
// ============================================================================

window.deleteDistributor = async function(userId, userName) {
    if (!confirm(`Are you sure you want to delete distributor "${userName}"?`)) return;

    const token = localStorage.getItem('admin_token');
    if (!token) return;

    toggleLoader(true);
    try {
        const url = API_ENDPOINTS.UPDATE_USER(userId, 'distributor');
        const response = await fetch(url, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await response.json();
        toggleLoader(false);

        if (!response.ok) throw new Error(data.detail || 'Failed to delete distributor');

        showToast(`Distributor "${userName}" has been deleted`);
        if (typeof window.fetchUsers === 'function') window.fetchUsers();
    } catch (err) {
        toggleLoader(false);
        showToast(err.message, 'error');
    }
};
