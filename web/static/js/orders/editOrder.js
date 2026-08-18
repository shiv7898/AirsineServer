// ============================================================================
// editOrder.js - Edit Order details (Modern UI)
// ============================================================================

function openEditOrderPage(orderId) {
  if (!window.adminOrders || window.adminOrders.length === 0) {
    showToast("Order data not available. Please refresh the page.", "error");
    return;
  }

  const order = window.adminOrders.find((o) => o.id === orderId);
  if (!order) {
    showToast("Order not found", "error");
    return;
  }

  const container = document.getElementById("edit-order-container");

  // Update URL
  history.pushState(null, '', '/orders/edit/' + orderId);

  // Safely extract product and user data
  const product = order.product || {};
  const user = order.user || {};
  const userInitials = (user.name || order.customer_name || "U")
    .substring(0, 2)
    .toUpperCase();

  // We parse status down to 0, 1, 2 for the select box
  let statusCode = "0";
  if (order.status === "APPROVED" || order.status === 1) statusCode = "1";
  if (order.status === "DELIVERED" || order.status === 2) statusCode = "2";

  container.innerHTML = `
        <style>
            .ud-container { display: flex; flex-direction: column; gap: 24px; animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); margin-top: 25px; }
            .ud-card { background: var(--bg-glass, rgba(255,255,255,0.95)); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--border-glass, rgba(226,232,240,0.8)); border-radius: 20px; padding: 24px; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05); }
            .ud-card-title { margin-top: 0; margin-bottom: 20px; color: var(--text-primary, #0f172a); font-size: 14px; font-weight: 700; border-bottom: 1px solid rgba(226, 232, 240, 0.6); padding-bottom: 12px; display: flex; align-items: center; gap: 8px; }
            .ud-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }
            .ud-field { display: flex; flex-direction: column; position: relative; }
            .ud-label { font-size: 10px; color: var(--text-muted, #64748b); font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px; }
            .ud-value { font-size: 13px; font-weight: 600; color: var(--text-primary, #0f172a); padding: 8px 12px; background: rgba(248, 250, 252, 0.6); border: 1px solid rgba(226, 232, 240, 0.5); border-radius: 12px; min-height: 38px; display: flex; align-items: center; box-sizing: border-box; }
            .ud-badge { padding: 5px 12px; border-radius: 20px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; display: inline-flex; align-items: center; gap: 6px; }
        </style>
        
        <div class="ud-container" style="width: 100%; margin: 10 auto; ">
            
            <!-- Update Status Card -->
            <div class="ud-card" style="border-top: 5px solid #3b82f6;">
                <h3 class="ud-card-title"><i class="fa-solid fa-pen-to-square" style="color: #3b82f6;"></i> Update Order Status</h3>
                <form id="edit-order-form" onsubmit="submitEditOrder(event)">
                    <input type="hidden" id="eo-id" value="${order.id}">
                    <div class="ud-grid">
                        <div class="ud-field">
                            <label class="ud-label" for="eo-status">Select New Status</label>
                            <select id="eo-status" class="ud-input" style="cursor: pointer;">
                                <option value="0" ${statusCode === "0" ? "selected" : ""}>⏳ Pending (Waiting for Approval)</option>
                                <option value="1" ${statusCode === "1" ? "selected" : ""}>⚙️ Approved (Processing)</option>
                                <option value="2" ${statusCode === "2" ? "selected" : ""}>✅ Delivered (Completed)</option>
                            </select>
                        </div>
                        <div class="ud-field" style="justify-content: flex-end;">
                            <button type="submit" class="ud-btn ud-btn-primary" style="height: 42px;">
                                <i class="fa-solid fa-floppy-disk"></i> SAVE CHANGES
                            </button>
                        </div>
                    </div>
                </form>
            </div>
            
            <!-- Product Details Card -->
            <div class="ud-card">
                <h3 class="ud-card-title"><i class="fa-solid fa-box-open" style="color: #6366f1;"></i> Product Details</h3>
                <div class="ud-grid">
                    <div class="ud-field">
                        <div class="ud-label">Product Name</div>
                        <div class="ud-value">${product.product_name || order.product_name || "N/A"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Brand / Model</div>
                        <div class="ud-value">${product.brand || "-"} / ${product.model_name || "-"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Category</div>
                        <div class="ud-value">${product.product_type || "-"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Unit Price</div>
                        <div class="ud-value">₹${product.unit_price || "-"}</div>
                    </div>
                </div>
            </div>
            
            <!-- Payment Summary Card -->
            <div class="ud-card">
                <h3 class="ud-card-title"><i class="fa-solid fa-receipt" style="color: #10b981;"></i> Payment Summary</h3>
                <div class="ud-grid">
                    <div class="ud-field">
                        <div class="ud-label">Quantity</div>
                        <div class="ud-value">${order.quantity || 1}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Total MRP</div>
                        <div class="ud-value">₹${(order.mrp_amount || order.total_amount || 0).toFixed(2)}</div>
                    </div>
                    ${
                      order.mrp_discount_amount ||
                      (order.mrp_amount &&
                        order.mrp_amount > order.total_amount)
                        ? `
                    <div class="ud-field">
                        <div class="ud-label">MRP Discount</div>
                        <div class="ud-value" style="color: #10b981;">- ₹${(order.mrp_discount_amount || order.mrp_amount - order.total_amount).toFixed(2)}</div>
                    </div>`
                        : ""
                    }
                    <div class="ud-field">
                        <div class="ud-label">Selling Price (Subtotal)</div>
                        <div class="ud-value">₹${(order.total_amount || 0).toFixed(2)}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">GST Amount</div>
                        <div class="ud-value">₹${order.gst_amount ? order.gst_amount.toFixed(2) : "0.00"}</div>
                    </div>
                    ${
                      order.product_discount_amount
                        ? `
                    <div class="ud-field">
                        <div class="ud-label">Role/Customer Discount</div>
                        <div class="ud-value" style="color: #ef4444;">- ₹${order.product_discount_amount.toFixed(2)}</div>
                    </div>`
                        : ""
                    }
                    ${
                      order.referral_discount_amount
                        ? `
                    <div class="ud-field">
                        <div class="ud-label">Referral Discount</div>
                        <div class="ud-value" style="color: #ec4899;">- ₹${order.referral_discount_amount.toFixed(2)}</div>
                    </div>`
                        : ""
                    }
                    <div class="ud-field" style="grid-column: 1 / -1; max-width: 300px;">
                        <div class="ud-label">Final Amount</div>
                        <div class="ud-value" style="font-size: 16px; font-weight: 800; color: #10b981; background: rgba(16,185,129,0.05); border-color: rgba(16,185,129,0.2);">₹${order.final_amount || "0.00"}</div>
                    </div>
                </div>
            </div>
            
            <!-- Customer Details Card -->
            <div class="ud-card">
                <h3 class="ud-card-title"><i class="fa-solid fa-circle-user" style="color: #8b5cf6;"></i> Customer Details</h3>
                <div class="ud-grid">
                    <div class="ud-field">
                        <div class="ud-label">Full Name</div>
                        <div class="ud-value">${user.name || order.customer_name || "N/A"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Email Address</div>
                        <div class="ud-value">${user.email || "N/A"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Phone Number</div>
                        <div class="ud-value">${user.phone || order.customer_phone || "N/A"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Custom ID</div>
                        <div class="ud-value">${user.custom_id || "-"}</div>
                    </div>
                </div>
            </div>
            
            <!-- Shipping Address Card -->
            <div class="ud-card">
                <h3 class="ud-card-title"><i class="fa-solid fa-truck-fast" style="color: #ec4899;"></i> Shipping Address</h3>
                <div class="ud-grid">
                    <div class="ud-field">
                        <div class="ud-label">Building / Flat</div>
                        <div class="ud-value">${order.building || "-"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Locality / Area</div>
                        <div class="ud-value">${order.locality || "-"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">District & State</div>
                        <div class="ud-value">${order.district || "-"}, ${order.state || "-"}</div>
                    </div>
                    <div class="ud-field">
                        <div class="ud-label">Pincode</div>
                        <div class="ud-value">${order.pincode || "-"}</div>
                    </div>
                    ${
                      order.referral_code
                        ? `
                    <div class="ud-field">
                        <div class="ud-label">Referral Code Used</div>
                        <div class="ud-value" style="color: #ec4899; font-weight: 700;">${order.referral_code}</div>
                    </div>
                    `
                        : ""
                    }
                </div>
            </div>
            
        </div>
    `;

  switchTab("edit-order-view");
}

async function submitEditOrder(e) {
  e.preventDefault();
  const orderId = document.getElementById("eo-id").value;
  const newStatus = parseInt(document.getElementById("eo-status").value);

  if (!orderId) {
    showToast("Invalid Order ID", "error");
    return;
  }

  const token = localStorage.getItem("admin_token");
  toggleLoader(true);
  try {
    const response = await fetch(
      `${API_ENDPOINTS.ORDERS}/${orderId}/status?status=${newStatus}`,
      {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}` },
      },
    );

    const data = await response.json();
    toggleLoader(false);

    if (response.ok) {
      showToast("Order status updated successfully", "success");
      fetchOrders();
      switchTab("orders-view");
    } else {
      showToast(data.detail || "Failed to update order", "error");
    }
  } catch (err) {
    toggleLoader(false);
    showToast(err.message, "error");
  }
}
