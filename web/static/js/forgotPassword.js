/**
 * ============================================================================
 * forgotPassword.js - Admin & Sub-Admin Web Password Reset Handler
 * ============================================================================
 * One-by-One Window Progression:
 *   Stage 1: Enter Email -> Send Code
 *   Stage 2: Enter & Verify 6-digit OTP -> Retrieve Reset Token
 *   Stage 3: Set New Password & Confirm -> Update Account
 *   Stage 4: Success Confirmation Popup -> Return to Sign In
 */

let forgotEmail = '';
let forgotResetToken = null;
let forgotCooldownTimer = null;
let forgotCooldownSeconds = 0;

/**
 * Open the Forgot Password Modal
 */
function openForgotPasswordModal(e) {
  if (e) e.preventDefault();

  const modal = document.getElementById('forgot-password-modal');
  if (!modal) return;

  // Pre-fill email if user already typed it in login form
  const loginEmailInput = document.getElementById('login-email');
  const forgotEmailInput = document.getElementById('forgot-input-email');
  if (loginEmailInput && loginEmailInput.value.trim() && forgotEmailInput) {
    forgotEmailInput.value = loginEmailInput.value.trim();
  }

  // Always reset to initial email window
  forgotResetToken = null;
  switchStage('email');
  modal.classList.add('active');

  setTimeout(() => {
    if (forgotEmailInput) forgotEmailInput.focus();
  }, 180);

  setupWebOtpInputListeners();
}

/**
 * Close the Forgot Password Modal
 */
function closeForgotPasswordModal() {
  const modal = document.getElementById('forgot-password-modal');
  if (!modal) return;
  modal.classList.remove('active');

  if (forgotCooldownTimer) {
    clearInterval(forgotCooldownTimer);
    forgotCooldownTimer = null;
  }
}

/**
 * Switch Between Windows ('email', 'otp', 'password', 'success')
 */
function switchStage(stage) {
  const stageEmail = document.getElementById('forgot-stage-email');
  const stageOtp = document.getElementById('forgot-stage-otp');
  const stagePassword = document.getElementById('forgot-stage-password');
  const stageSuccess = document.getElementById('forgot-stage-success');

  const stepNav1 = document.getElementById('step-nav-1');
  const stepNav2 = document.getElementById('step-nav-2');
  const stepNav3 = document.getElementById('step-nav-3');
  const conn1 = document.getElementById('connector-1');
  const conn2 = document.getElementById('connector-2');
  const stepsBar = document.getElementById('forgot-steps-bar');

  const modalTitle = document.getElementById('forgot-modal-title');
  const modalSub = document.getElementById('forgot-modal-sub');
  const headerIcon = document.getElementById('forgot-header-icon');

  // Hide all stages
  [stageEmail, stageOtp, stagePassword, stageSuccess].forEach((s) => s && s.classList.remove('active'));

  // Reset navigation states
  [stepNav1, stepNav2, stepNav3].forEach((nav) => nav && nav.classList.remove('active', 'completed'));
  [conn1, conn2].forEach((c) => c && c.classList.remove('active'));

  if (stage === 'email') {
    if (stageEmail) stageEmail.classList.add('active');
    if (stepsBar) stepsBar.style.display = 'flex';
    if (stepNav1) stepNav1.classList.add('active');

    if (modalTitle) modalTitle.textContent = 'Admin Account Recovery';
    if (modalSub) modalSub.textContent = 'Enter your administrative email to receive an OTP';
    if (headerIcon) headerIcon.innerHTML = '<i class="fa-solid fa-user-shield"></i>';

    setTimeout(() => {
      const emailInput = document.getElementById('forgot-input-email');
      if (emailInput) emailInput.focus();
    }, 150);
  } else if (stage === 'otp') {
    if (stageOtp) stageOtp.classList.add('active');
    if (stepsBar) stepsBar.style.display = 'flex';
    if (stepNav1) stepNav1.classList.add('completed');
    if (conn1) conn1.classList.add('active');
    if (stepNav2) stepNav2.classList.add('active');

    if (modalTitle) modalTitle.textContent = 'Two-Factor Verification';
    if (modalSub) modalSub.textContent = 'Enter the 6-digit code sent to your email';
    if (headerIcon) headerIcon.innerHTML = '<i class="fa-solid fa-key"></i>';

    // Auto-focus first OTP box
    setTimeout(() => {
      const firstOtp = document.getElementById('web-otp-0');
      if (firstOtp) firstOtp.focus();
    }, 180);
  } else if (stage === 'password') {
    if (stagePassword) stagePassword.classList.add('active');
    if (stepsBar) stepsBar.style.display = 'flex';
    if (stepNav1) stepNav1.classList.add('completed');
    if (conn1) conn1.classList.add('active');
    if (stepNav2) stepNav2.classList.add('completed');
    if (conn2) conn2.classList.add('active');
    if (stepNav3) stepNav3.classList.add('active');

    if (modalTitle) modalTitle.textContent = 'Set New Password';
    if (modalSub) modalSub.textContent = 'Choose a secure password for your administrator account';
    if (headerIcon) headerIcon.innerHTML = '<i class="fa-solid fa-lock"></i>';

    // Auto-focus new password input
    setTimeout(() => {
      const newPwdInput = document.getElementById('forgot-new-pwd');
      if (newPwdInput) newPwdInput.focus();
    }, 180);
  } else if (stage === 'success') {
    if (stageSuccess) stageSuccess.classList.add('active');
    if (stepsBar) stepsBar.style.display = 'none';

    if (modalTitle) modalTitle.textContent = 'Account Secured';
    if (modalSub) modalSub.textContent = 'Your password has been updated successfully';
    if (headerIcon) headerIcon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
  }
}

/**
 * Window 1: Send OTP to Administrator Email
 */
async function handleSendVerificationCode(e) {
  if (e) e.preventDefault();

  const emailInput = document.getElementById('forgot-input-email');
  const btn = document.getElementById('btn-send-code');
  const email = emailInput ? emailInput.value.trim().toLowerCase() : '';

  if (!email) {
    if (typeof showToast === 'function') showToast('Please enter your administrator email', 'error');
    return;
  }

  forgotEmail = email;
  const originalBtnHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Sending Code...</span>';

  try {
    const endpoint = (window.API_ENDPOINTS && window.API_ENDPOINTS.FORGOT_PASSWORD) || '/api/v1/web/auth/forgot-password';

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();

    if (!response.ok) {
      const errMsg = (data.error && data.error.message) || data.detail || 'Could not send verification code';
      throw new Error(errMsg);
    }

    if (typeof showToast === 'function') {
      showToast('6-digit verification code sent to your email!', 'success');
    }

    // Set email display in Window 2
    const displayEl = document.getElementById('forgot-target-email-display');
    if (displayEl) displayEl.textContent = forgotEmail;

    // Reset OTP boxes
    for (let i = 0; i < 6; i++) {
      const box = document.getElementById(`web-otp-${i}`);
      if (box) {
        box.value = '';
        box.classList.remove('filled');
      }
    }

    startWebResendTimer(60);
    // Move to Window 2: OTP
    switchStage('otp');
  } catch (err) {
    if (typeof showToast === 'function') {
      showToast(err.message, 'error');
    } else {
      alert(err.message);
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalBtnHtml;
  }
}

/**
 * Window 2: Verify 6-Digit OTP Code
 */
async function handleVerifyOtpCode(e) {
  if (e) e.preventDefault();

  // Gather 6-digit OTP
  let otp = '';
  for (let i = 0; i < 6; i++) {
    const box = document.getElementById(`web-otp-${i}`);
    if (box) otp += box.value.trim();
  }

  if (otp.length !== 6) {
    if (typeof showToast === 'function') {
      showToast('Please enter the complete 6-digit verification code', 'error');
    }
    const firstEmpty = document.querySelector('.forgot-otp-box:not(.filled)');
    if (firstEmpty) firstEmpty.focus();
    return;
  }

  const btn = document.getElementById('btn-verify-otp');
  const originalBtnHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Verifying Code...</span>';

  try {
    const endpoint = (window.API_ENDPOINTS && window.API_ENDPOINTS.VERIFY_OTP) || '/api/v1/web/auth/verify-otp';

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: forgotEmail,
        otp: otp,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      const errMsg = (data.error && data.error.message) || data.detail || 'Invalid or expired verification code';
      throw new Error(errMsg);
    }

    // Save reset token for Window 3
    forgotResetToken = data.reset_token || null;

    if (typeof showToast === 'function') {
      showToast('Verification code confirmed!', 'success');
    }

    // Clear password fields
    const newPwd = document.getElementById('forgot-new-pwd');
    const confirmPwd = document.getElementById('forgot-confirm-pwd');
    if (newPwd) newPwd.value = '';
    if (confirmPwd) confirmPwd.value = '';
    validateWebPasswordCriteria();

    // Advance to Window 3: Set New Password
    switchStage('password');
  } catch (err) {
    if (typeof showToast === 'function') {
      showToast(err.message, 'error');
    } else {
      alert(err.message);
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalBtnHtml;
  }
}

/**
 * Window 3: Finalize Password Reset
 */
async function handleFinalizePasswordReset(e) {
  if (e) e.preventDefault();

  const newPassword = document.getElementById('forgot-new-pwd').value;
  const confirmPassword = document.getElementById('forgot-confirm-pwd').value;

  if (newPassword.length < 6) {
    if (typeof showToast === 'function') showToast('Password must be at least 6 characters long', 'error');
    return;
  }

  if (!/[A-Za-z]/.test(newPassword) || !/[0-9]/.test(newPassword)) {
    if (typeof showToast === 'function') showToast('Password must contain both letters and numbers', 'error');
    return;
  }

  if (newPassword !== confirmPassword) {
    if (typeof showToast === 'function') showToast('Passwords do not match', 'error');
    return;
  }

  const btn = document.getElementById('btn-submit-reset');
  const originalBtnHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Securing Account...</span>';

  try {
    const endpoint = (window.API_ENDPOINTS && window.API_ENDPOINTS.RESET_PASSWORD) || '/api/v1/web/auth/reset-password';

    const payload = {
      email: forgotEmail,
      new_password: newPassword,
      confirm_password: confirmPassword,
    };

    if (forgotResetToken) {
      payload.reset_token = forgotResetToken;
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      const errMsg = (data.error && data.error.message) || data.detail || 'Password reset failed';
      throw new Error(errMsg);
    }

    if (typeof showToast === 'function') {
      showToast('Password updated successfully!', 'success');
    }

    // Advance to Window 4: Success Popup
    switchStage('success');
  } catch (err) {
    if (typeof showToast === 'function') {
      showToast(err.message, 'error');
    } else {
      alert(err.message);
    }
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalBtnHtml;
  }
}

/**
 * Resend Verification OTP
 */
async function handleWebResendOtp() {
  if (forgotCooldownSeconds > 0) return;

  const btn = document.getElementById('web-btn-resend');
  btn.disabled = true;

  try {
    const endpoint = (window.API_ENDPOINTS && window.API_ENDPOINTS.RESEND_OTP) || '/api/v1/web/auth/resend-otp';

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: forgotEmail }),
    });

    const data = await response.json();

    if (!response.ok) {
      const errMsg = (data.error && data.error.message) || data.detail || 'Could not resend verification code';
      throw new Error(errMsg);
    }

    if (typeof showToast === 'function') {
      showToast('A fresh 6-digit code has been sent to your email', 'success');
    }

    // Clear existing OTP inputs
    for (let i = 0; i < 6; i++) {
      const box = document.getElementById(`web-otp-${i}`);
      if (box) {
        box.value = '';
        box.classList.remove('filled');
      }
    }

    startWebResendTimer(60);
    const firstOtp = document.getElementById('web-otp-0');
    if (firstOtp) firstOtp.focus();
  } catch (err) {
    if (typeof showToast === 'function') showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
  }
}

/**
 * Resend Countdown Timer
 */
function startWebResendTimer(seconds) {
  forgotCooldownSeconds = seconds;
  const countdownEl = document.getElementById('web-resend-countdown');
  const timerSecEl = document.getElementById('web-resend-timer-sec');
  const resendBtn = document.getElementById('web-btn-resend');

  if (countdownEl) countdownEl.style.display = 'inline';
  if (resendBtn) resendBtn.style.display = 'none';
  if (timerSecEl) timerSecEl.textContent = forgotCooldownSeconds;

  if (forgotCooldownTimer) clearInterval(forgotCooldownTimer);

  forgotCooldownTimer = setInterval(() => {
    forgotCooldownSeconds--;
    if (timerSecEl) timerSecEl.textContent = forgotCooldownSeconds;

    if (forgotCooldownSeconds <= 0) {
      clearInterval(forgotCooldownTimer);
      forgotCooldownTimer = null;
      if (countdownEl) countdownEl.style.display = 'none';
      if (resendBtn) resendBtn.style.display = 'inline-flex';
    }
  }, 1000);
}

/**
 * Window 4: Finish Reset and Return to Sign In
 */
function finishPasswordReset() {
  closeForgotPasswordModal();

  // Pre-fill email in login form
  const loginEmail = document.getElementById('login-email');
  const loginPassword = document.getElementById('login-password');
  if (loginEmail && forgotEmail) {
    loginEmail.value = forgotEmail;
  }
  if (loginPassword) {
    loginPassword.value = '';
    setTimeout(() => loginPassword.focus(), 250);
  }

  if (typeof showToast === 'function') {
    showToast('Please sign in with your new password', 'info');
  }
}

/**
 * Real-Time Password Criteria Validation
 */
function validateWebPasswordCriteria() {
  const newPwd = document.getElementById('forgot-new-pwd')?.value || '';
  const confirmPwd = document.getElementById('forgot-confirm-pwd')?.value || '';

  const ruleLength = document.getElementById('rule-length');
  const ruleChars = document.getElementById('rule-chars');
  const ruleMatch = document.getElementById('rule-match');

  // Length check (6+ chars)
  if (ruleLength) {
    if (newPwd.length >= 6) ruleLength.classList.add('valid');
    else ruleLength.classList.remove('valid');
  }

  // Letters and numbers check
  if (ruleChars) {
    if (/[A-Za-z]/.test(newPwd) && /[0-9]/.test(newPwd)) ruleChars.classList.add('valid');
    else ruleChars.classList.remove('valid');
  }

  // Matching check
  if (ruleMatch) {
    if (newPwd.length > 0 && newPwd === confirmPwd) ruleMatch.classList.add('valid');
    else ruleMatch.classList.remove('valid');
  }
}

/**
 * Toggle Password Visibility (Eye Icon)
 */
function toggleWebPasswordVisibility(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;

  const icon = btn.querySelector('i');
  if (input.type === 'password') {
    input.type = 'text';
    if (icon) {
      icon.classList.remove('fa-eye');
      icon.classList.add('fa-eye-slash');
    }
  } else {
    input.type = 'password';
    if (icon) {
      icon.classList.remove('fa-eye-slash');
      icon.classList.add('fa-eye');
    }
  }
}

/**
 * Setup 6-Box OTP Keyboard Navigation & Paste Handling
 */
function setupWebOtpInputListeners() {
  for (let i = 0; i < 6; i++) {
    const box = document.getElementById(`web-otp-${i}`);
    if (!box) continue;

    // Handle single digit and forward focus
    box.oninput = (e) => {
      const val = box.value.replace(/[^0-9]/g, '');
      box.value = val ? val[0] : '';

      if (box.value) {
        box.classList.add('filled');
        if (i < 5) {
          const next = document.getElementById(`web-otp-${i + 1}`);
          if (next) next.focus();
        }
      } else {
        box.classList.remove('filled');
      }
    };

    // Handle backspace navigation
    box.onkeydown = (e) => {
      if (e.key === 'Backspace' && !box.value && i > 0) {
        const prev = document.getElementById(`web-otp-${i - 1}`);
        if (prev) {
          prev.focus();
          prev.value = '';
          prev.classList.remove('filled');
        }
      }
    };

    // Handle paste of 6-digit code
    box.onpaste = (e) => {
      e.preventDefault();
      const pasteData = (e.clipboardData || window.clipboardData).getData('text');
      const digits = pasteData.replace(/[^0-9]/g, '').slice(0, 6);

      for (let j = 0; j < digits.length; j++) {
        const targetBox = document.getElementById(`web-otp-${j}`);
        if (targetBox) {
          targetBox.value = digits[j];
          targetBox.classList.add('filled');
        }
      }

      if (digits.length === 6) {
        const lastBox = document.getElementById('web-otp-5');
        if (lastBox) lastBox.focus();
      }
    };
  }
}

// Close modal when clicking backdrop or pressing Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeForgotPasswordModal();
  }
});

document.addEventListener('click', (e) => {
  const modal = document.getElementById('forgot-password-modal');
  if (modal && e.target === modal) {
    closeForgotPasswordModal();
  }
});

// Make functions globally available for inline event handlers
window.openForgotPasswordModal = openForgotPasswordModal;
window.closeForgotPasswordModal = closeForgotPasswordModal;
window.switchStage = switchStage;
window.handleSendVerificationCode = handleSendVerificationCode;
window.handleVerifyOtpCode = handleVerifyOtpCode;
window.handleFinalizePasswordReset = handleFinalizePasswordReset;
window.handleWebResendOtp = handleWebResendOtp;
window.finishPasswordReset = finishPasswordReset;
window.validateWebPasswordCriteria = validateWebPasswordCriteria;
window.toggleWebPasswordVisibility = toggleWebPasswordVisibility;
