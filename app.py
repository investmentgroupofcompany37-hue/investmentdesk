<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>InvestDesk · Admin · Full CRUD</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      font-family: 'Inter', system-ui, sans-serif;
      color: #0b1b33;
      line-height: 1.5;
      min-height: 100vh;
      background: #f0f4fe;
    }
    .login-shell {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      position: relative;
      background:
        linear-gradient(135deg, rgba(11, 27, 51, 0.75) 0%, rgba(37, 99, 235, 0.40) 60%, rgba(11, 27, 51, 0.70) 100%),
        url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=2070&auto=format&fit=crop') center/cover no-repeat;
    }
    .login-shell::before {
      content: '';
      position: absolute;
      inset: 0;
      backdrop-filter: blur(2px);
      z-index: 0;
    }
    .login-card {
      position: relative;
      z-index: 1;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(12px);
      padding: 2.5rem 2.5rem 2rem;
      border-radius: 36px;
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(255, 255, 255, 0.3);
      max-width: 400px;
      width: 100%;
    }
    .login-card .mark {
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 700;
      font-size: 1.8rem;
      letter-spacing: -0.03em;
      color: #0b1b33;
      text-align: center;
      margin-bottom: 0.2rem;
    }
    .login-card .mark svg {
      width: 32px;
      height: 32px;
      fill: #2563eb;
      vertical-align: middle;
      margin-right: 0.2rem;
    }
    .login-card h1 {
      font-size: 1.2rem;
      font-weight: 600;
      text-align: center;
      color: #475569;
      margin-bottom: 1.5rem;
    }
    .login-error {
      background: #fef2f2;
      color: #dc2626;
      padding: 0.5rem 1rem;
      border-radius: 12px;
      font-size: 0.8rem;
      margin-bottom: 1rem;
      display: none;
    }
    .login-error.show { display: block; }
    .login-card .field { margin-bottom: 1rem; }
    .login-card .field label {
      display: block;
      font-size: 0.8rem;
      font-weight: 500;
      color: #334155;
      margin-bottom: 0.2rem;
    }
    .login-card .field input {
      width: 100%;
      padding: 0.7rem 1rem;
      border-radius: 14px;
      border: 1px solid #d0d9e6;
      background: rgba(255, 255, 255, 0.8);
      font-size: 0.95rem;
      font-family: 'Inter', sans-serif;
      transition: 0.12s;
    }
    .login-card .field input:focus {
      outline: none;
      border-color: #2563eb;
      box-shadow: 0 0 0 3px rgba(37,99,235,0.15);
      background: white;
    }
    .btn {
      background: transparent;
      border: 1px solid #d0d9e6;
      padding: 0.5rem 1.2rem;
      border-radius: 40px;
      font-weight: 500;
      font-size: 0.85rem;
      cursor: pointer;
      transition: 0.15s;
      color: #1e293b;
      font-family: 'Inter', sans-serif;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }
    .btn-primary { background: #2563eb; border-color: #2563eb; color: white; }
    .btn-primary:hover { background: #1d4ed8; }
    .btn-danger { background: #dc2626; border-color: #dc2626; color: white; }
    .btn-danger:hover { background: #b91c1c; }
    .btn-sm { padding: 0.3rem 0.8rem; font-size: 0.75rem; }
    .btn-success { background: #16a34a; border-color: #16a34a; color: white; }
    .btn-success:hover { background: #15803d; }
    .hidden { display: none !important; }

    .admin-wrapper {
      max-width: 1440px;
      margin: 0 auto;
      padding: 1.5rem;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .ticker-tape {
      background: #0b1b33;
      color: #b9c8e0;
      padding: 0.5rem 0;
      overflow: hidden;
      white-space: nowrap;
      border-radius: 16px 16px 0 0;
      font-size: 0.85rem;
      letter-spacing: 0.01em;
      flex-shrink: 0;
    }
    .ticker-track {
      display: inline-flex;
      gap: 2.8rem;
      animation: tickerScroll 36s linear infinite;
      padding-left: 2rem;
    }
    .ticker-item .sym { font-weight: 600; color: #f0f4ff; }
    .ticker-item .change-up { color: #4ade80; }
    .ticker-item .change-down { color: #f87171; }
    @keyframes tickerScroll { 0% { transform:translateX(0); } 100% { transform:translateX(-50%); } }

    .shell {
      background: #ffffff;
      border-radius: 0 0 32px 32px;
      box-shadow: 0 20px 60px rgba(0,20,50,0.06);
      border: 1px solid #e8edf6;
      border-top: none;
      display: flex;
      flex-wrap: wrap;
      flex: 1;
    }
    .rail {
      width: 230px;
      background: #fafcff;
      padding: 2rem 1.2rem 1.5rem;
      border-right: 1px solid #e8edf6;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
    .rail-brand .mark {
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 700;
      font-size: 1.6rem;
      letter-spacing: -0.03em;
      color: #0b1b33;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }
    .rail-brand .mark svg { width: 28px; height: 28px; fill: #2563eb; }
    .rail-brand .sub { font-size: 0.7rem; color: #64748b; letter-spacing: 0.04em; margin-top: 0.1rem; padding-left: 0.2rem; }
    .rail-nav { margin: 2.2rem 0 1.8rem; display:flex; flex-direction:column; gap:0.4rem; }
    .rail-link {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      padding: 0.6rem 0.75rem;
      border-radius: 12px;
      color: #64748b;
      text-decoration: none;
      font-weight: 500;
      font-size: 0.9rem;
      transition: 0.15s;
    }
    .rail-link svg { width: 20px; height: 20px; fill: currentColor; flex-shrink: 0; }
    .rail-link.active { background: #dbeafe; color: #2563eb; font-weight: 600; }
    .rail-link:hover:not(.active) { background: #f1f5f9; }
    .rail-foot {
      margin-top: auto;
      font-size: 0.75rem;
      color: #64748b;
      border-top: 1px solid #e8edf6;
      padding-top: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    .main {
      flex: 1;
      padding: 1.8rem 2rem 2rem;
      background: #ffffff;
      min-width: 0;
    }
    .main-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1.8rem;
    }
    .main-header h1 {
      font-size: 1.6rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .main-header h1 svg { width: 28px; height: 28px; fill: #2563eb; }
    .live-dot {
      display: inline-block;
      width: 10px;
      height: 10px;
      background: #22c55e;
      border-radius: 50%;
      box-shadow: 0 0 0 3px #dcfce7;
      animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot { 0% { opacity:1; } 50% { opacity:0.5; } 100% { opacity:1; } }
    .meta { color: #64748b; font-size: 0.8rem; background: #f1f5f9; padding: 0.3rem 1rem; border-radius: 40px; }
    .summary-strip {
      display: grid;
      grid-template-columns: repeat(4,1fr);
      gap: 0.8rem;
      margin-bottom: 2rem;
    }
    .summary-cell {
      background: #f8fafc;
      padding: 0.8rem 1rem;
      border-radius: 16px;
      border: 1px solid #e8edf6;
      display: flex;
      flex-direction: column;
    }
    .summary-cell .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b; }
    .summary-cell .value { font-size: 1.2rem; font-weight: 600; margin-top: 0.15rem; }
    .error-banner {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
      padding: 0.8rem 1.2rem;
      border-radius: 12px;
      margin-bottom: 1rem;
      display: none;
      font-size: 0.85rem;
      align-items: center;
      gap: 0.8rem;
      flex-wrap: wrap;
    }
    .error-banner.show { display: flex; }
    .error-banner .retry-btn {
      background: #b91c1c;
      color: white;
      border: none;
      padding: 0.3rem 1rem;
      border-radius: 40px;
      font-weight: 600;
      cursor: pointer;
      font-family: 'Inter', sans-serif;
      font-size: 0.75rem;
    }
    .error-banner .retry-btn:hover { background: #991b1b; }
    .panel {
      background: #fafcff;
      border-radius: 20px;
      border: 1px solid #e8edf6;
      padding: 1.2rem 1.2rem 0.5rem;
      margin-top: 1rem;
    }
    .panel-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }
    .panel-head h2 { font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; gap: 0.4rem; }
    .panel-head h2 svg { width: 22px; height: 22px; fill: #2563eb; }
    table { width:100%; border-collapse:collapse; font-size:0.85rem; }
    th { text-align:left; padding:0.5rem 0.25rem; color:#64748b; font-weight:500; border-bottom:1px solid #e8edf6; }
    td { padding:0.6rem 0.25rem; border-bottom:1px solid #f1f5f9; vertical-align:middle; }
    .empty-state { text-align:center; padding:2rem 0; color:#64748b; }
    .empty-state .icon { font-size:2rem; opacity:0.4; }
    .actions-cell { display: flex; gap: 0.3rem; flex-wrap: wrap; }
    .btn-icon {
      background: transparent;
      border: none;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
      border-radius: 20px;
      font-size: 0.7rem;
      font-weight: 500;
      transition: 0.12s;
      display: inline-flex;
      align-items: center;
      gap: 0.2rem;
      border: 1px solid transparent;
    }
    .btn-icon:hover { opacity: 0.75; transform: scale(1.05); }
    .btn-icon.edit { background: #dbeafe; color: #1d4ed8; border-color: #b9d0f6; }
    .btn-icon.delete { background: #fee2e2; color: #b91c1c; border-color: #fecaca; }
    .btn-icon.create { background: #dcfce7; color: #15803d; border-color: #bbf7d0; }
    .btn-icon svg { width: 14px; height: 14px; fill: currentColor; }
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.3);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 999;
    }
    .modal-overlay.hidden { display: none; }
    .modal {
      background: white;
      padding: 2rem;
      border-radius: 32px;
      max-width: 420px;
      width: 100%;
      box-shadow: 0 20px 48px rgba(0,0,0,0.12);
    }
    .modal h3 { font-size: 1.2rem; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.4rem; }
    .modal h3 svg { width: 24px; height: 24px; fill: #2563eb; }
    .modal .field { margin-bottom: 0.8rem; }
    .modal .field label { display: block; font-size: 0.75rem; font-weight: 500; color: #475569; margin-bottom: 0.2rem; }
    .modal .field input, .modal .field select {
      width: 100%;
      padding: 0.5rem 0.75rem;
      border-radius: 14px;
      border: 1px solid #d0d9e6;
      background: white;
      font-family: 'Inter', sans-serif;
    }
    .modal-actions { display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 1.2rem; }
    .toast {
      position: fixed;
      top: 5rem;
      left: 50%;
      transform: translateX(-50%);
      background: #0b1a2f;
      color: white;
      padding: 0.7rem 2rem;
      border-radius: 60px;
      font-weight: 500;
      font-size: 0.9rem;
      box-shadow: 0 8px 30px rgba(0,0,0,0.12);
      opacity: 0;
      transition: opacity 0.25s, transform 0.25s;
      pointer-events: none;
      z-index: 1000;
    }
    .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
    .toast.error { background: #b91c1c; }
    .sync-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: #dcfce7;
      color: #15803d;
      padding: 0.2rem 0.8rem;
      border-radius: 40px;
      font-size: 0.7rem;
      font-weight: 600;
    }
    .sync-badge svg { width: 14px; height: 14px; fill: currentColor; }
    .user-badge { display: inline-block; background: #e0e7ff; color: #3730a3; padding: 0.1rem 0.5rem; border-radius: 12px; font-size: 0.7rem; font-weight: 500; }
    .loading-row td { text-align: center; padding: 2rem; color: #64748b; }
    .error-row td { text-align: center; padding: 2rem; color: #dc2626; }
    .loading-spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 0.6s ease-in-out infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    @media (max-width:860px) {
      .rail { width:100%; border-right:none; border-bottom:1px solid #e8edf6; }
      .main { padding: 1.2rem; }
      .summary-strip { grid-template-columns: 1fr 1fr; }
      .admin-wrapper { padding: 0.5rem; }
      .ticker-tape { border-radius: 0; }
      .shell { border-radius: 0; }
    }
    @media (max-width:600px) {
      .summary-strip { grid-template-columns: 1fr; }
      table { font-size: 0.7rem; }
      .actions-cell { flex-direction: row; gap: 0.2rem; }
      .btn-icon { font-size: 0.65rem; padding: 0.15rem 0.4rem; }
    }
  </style>
</head>
<body>
  <div class="toast" id="toast"></div>

  <!-- LOGIN -->
  <div class="login-shell" id="loginShell">
    <div class="login-card">
      <div class="mark">
        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/></svg>
        INVESTDESK
      </div>
      <h1>Admin Access</h1>
      <div class="login-error" id="loginError"></div>
      <div class="field">
        <label for="loginUsername">Username</label>
        <input type="text" id="loginUsername" placeholder="admin" autocomplete="username" />
      </div>
      <div class="field">
        <label for="loginPassword">Password</label>
        <input type="password" id="loginPassword" placeholder="••••••••" autocomplete="current-password" />
      </div>
      <button type="button" id="loginBtn" class="btn btn-primary" style="width:100%; margin-top:6px;">
        <span id="loginBtnText">Sign in</span>
        <span class="loading-spinner hidden" id="loginSpinner" style="display:none;"></span>
      </button>
      <div style="margin-top:1rem;text-align:center;font-size:0.7rem;color:#94a3b8;">
        Username: <strong>admin</strong> &nbsp;|&nbsp; Password: <strong>admin123</strong>
      </div>
    </div>
  </div>

  <!-- ADMIN SHELL -->
  <div class="hidden" id="adminShell">
    <div class="admin-wrapper">
      <div class="ticker-tape">
        <div class="ticker-track" id="tickerTrack">
          <div class="ticker-item"><span class="sym">TSLA</span> —</div>
          <div class="ticker-item"><span class="sym">AAPL</span> —</div>
          <div class="ticker-item"><span class="sym">NVDA</span> —</div>
          <div class="ticker-item"><span class="sym">MSFT</span> —</div>
        </div>
      </div>

      <div class="shell">
        <aside class="rail">
          <div class="rail-brand">
            <div class="mark">
              <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/></svg>
              INVESTDESK
            </div>
            <div class="sub">Admin · Full CRUD</div>
          </div>
          <nav class="rail-nav">
            <a class="rail-link" href="/dashboard" target="_blank">
              <svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
              Dashboard
            </a>
            <a class="rail-link active" href="#">
              <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/></svg>
              Admin panel
            </a>
          </nav>
          <div class="rail-foot">
            <button class="btn btn-sm btn-danger" id="logoutBtn" style="width:100%;">Sign out</button>
          </div>
        </aside>

        <main class="main">
          <div class="main-header">
            <h1>
              <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/></svg>
              <span class="live-dot"></span> Admin Panel
            </h1>
            <div style="display:flex; align-items:center; gap:0.8rem; flex-wrap:wrap;">
              <span class="sync-badge">
                <svg viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>
                Live Data
              </span>
              <span class="meta">Create · Edit · Delete</span>
            </div>
          </div>

          <div class="error-banner" id="errorBanner">
            <span id="errorMessage">⚠️ Failed to load data</span>
            <button class="retry-btn" id="retryBtn">🔄 Retry</button>
          </div>

          <div class="summary-strip">
            <div class="summary-cell"><div class="label">Total positions</div><div class="value" id="statTotalRows">—</div></div>
            <div class="summary-cell"><div class="label">Unique users</div><div class="value" id="statTotalUsers">—</div></div>
            <div class="summary-cell"><div class="label">Total invested</div><div class="value" id="statTotalInvested">—</div></div>
            <div class="summary-cell"><div class="label">Market value</div><div class="value" id="statTotalValue">—</div></div>
          </div>

          <div class="panel">
            <div class="panel-head">
              <h2>All Holdings</h2>
              <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
                <button class="btn btn-sm btn-success" id="createBtn">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                  New
                </button>
                <button class="btn btn-sm" id="refreshBtn">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>
                  Refresh
                </button>
                <button class="btn btn-sm btn-danger" id="resetDbBtn">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 5V2L8 6l4 4V7c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
                  Reset DB
                </button>
              </div>
            </div>
            <div style="overflow-x:auto;">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Email</th>
                    <th>Symbol</th>
                    <th>Shares</th>
                    <th>Buy price</th>
                    <th>Cost basis</th>
                    <th>Current price</th>
                    <th>Market value</th>
                    <th>Gain / loss</th>
                    <th style="min-width:130px;">Actions</th>
                  </tr>
                </thead>
                <tbody id="adminBody">
                  <tr class="loading-row"><td colspan="11">Loading investments...</td></tr>
                </tbody>
              </table>
            </div>
            <div class="empty-state hidden" id="adminEmpty">
              <div class="icon">◌</div>
              No records found. Click <strong>New</strong> to add one.
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>

  <!-- MODAL -->
  <div class="modal-overlay hidden" id="editModalOverlay">
    <div class="modal">
      <h3>
        <svg viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
        <span id="modalTitleText">Edit investment</span>
      </h3>
      <form id="editForm">
        <input type="hidden" id="editId" />
        <div class="field">
          <label for="editUserName">User Name *</label>
          <input type="text" id="editUserName" required placeholder="e.g. Kaka90" />
        </div>
        <div class="field">
          <label for="editEmail">Email</label>
          <input type="email" id="editEmail" placeholder="user@example.com" />
        </div>
        <div class="field">
          <label for="editSymbol">Symbol *</label>
          <select id="editSymbol" required>
            <option value="TSLA">TSLA — Tesla</option>
            <option value="AAPL">AAPL — Apple</option>
            <option value="NVDA">NVDA — NVIDIA</option>
            <option value="MSFT">MSFT — Microsoft</option>
          </select>
        </div>
        <div class="field">
          <label for="editShares">Shares *</label>
          <input type="number" id="editShares" step="0.0001" min="0.0001" required placeholder="e.g. 10" />
        </div>
        <div class="field">
          <label for="editBuyPrice">Buy Price ($) *</label>
          <input type="number" id="editBuyPrice" step="0.01" min="0.01" required placeholder="e.g. 150.00" />
        </div>
        <div class="modal-actions">
          <button type="button" class="btn" id="cancelEdit">Cancel</button>
          <button type="submit" class="btn btn-primary" id="modalSubmitBtn">Save</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    (function () {
      const ALLOWED_SYMBOLS = ['TSLA', 'AAPL', 'NVDA', 'MSFT'];
      let allInvestments = [];
      let pricesCache = {};
      let isLoading = false;
      let refreshInterval = null;

      // ── Toast ────────────────────────────────────────────────────────────
      const toastEl = document.getElementById('toast');
      let toastTimer = null;
      function showToast(msg, type = 'success') {
        if (toastTimer) clearTimeout(toastTimer);
        toastEl.textContent = msg;
        toastEl.className = 'toast ' + type + ' show';
        toastTimer = setTimeout(() => toastEl.classList.remove('show'), 3200);
      }

      // ── Error Banner ─────────────────────────────────────────────────────
      const errorBanner  = document.getElementById('errorBanner');
      const errorMessage = document.getElementById('errorMessage');
      function showError(msg) { errorMessage.textContent = '⚠️ ' + msg; errorBanner.classList.add('show'); }
      function hideError()    { errorBanner.classList.remove('show'); }

      // ── DOM refs ─────────────────────────────────────────────────────────
      const loginShell   = document.getElementById('loginShell');
      const adminShell   = document.getElementById('adminShell');
      const loginError   = document.getElementById('loginError');
      const loginUsername = document.getElementById('loginUsername');
      const loginPassword = document.getElementById('loginPassword');
      const loginBtnText  = document.getElementById('loginBtnText');
      const loginSpinner  = document.getElementById('loginSpinner');
      const loginBtn      = document.getElementById('loginBtn');

      // ── API helper ───────────────────────────────────────────────────────
      async function api(url, options = {}) {
        return fetch(url, {
          ...options,
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
        });
      }

      // ── Login ────────────────────────────────────────────────────────────
      async function doLogin() {
        loginError.classList.remove('show');
        loginError.textContent = '';

        const username = loginUsername.value.trim();
        const password = loginPassword.value.trim();

        if (!username || !password) {
          loginError.textContent = 'Please enter both username and password.';
          loginError.classList.add('show');
          return;
        }

        loginBtnText.textContent = 'Signing in…';
        loginSpinner.style.display = 'inline-block';
        loginBtn.disabled = true;

        try {
          const res  = await api('/api/admin/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
          });
          const data = await res.json();

          if (res.ok && data.ok) {
            onLoginSuccess();
          } else {
            // Server replied but rejected credentials
            loginError.textContent = data.error || 'Invalid username or password.';
            loginError.classList.add('show');
            loginPassword.value = '';
            loginPassword.focus();
          }
        } catch (err) {
          // Network / server down
          console.error('Login network error:', err);
          loginError.textContent =
            'Could not reach the server. Make sure Flask is running on http://localhost:5000';
          loginError.classList.add('show');
        } finally {
          loginBtnText.textContent = 'Sign in';
          loginSpinner.style.display = 'none';
          loginBtn.disabled = false;
        }
      }

      loginBtn.addEventListener('click', doLogin);
      loginPassword.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
      loginUsername.addEventListener('keydown', e => { if (e.key === 'Enter') loginPassword.focus(); });

      function onLoginSuccess() {
        loginShell.classList.add('hidden');
        adminShell.classList.remove('hidden');
        sessionStorage.setItem('admin_logged_in', 'true');
        showToast('✅ Welcome, Admin!', 'success');
        loadAdminData(true);
        updateTicker();
        if (refreshInterval) clearInterval(refreshInterval);
        refreshInterval = setInterval(() => {
          if (!adminShell.classList.contains('hidden')) {
            loadAdminData(false);
            updateTicker();
          }
        }, 30000);
      }

      // ── Logout ───────────────────────────────────────────────────────────
      document.getElementById('logoutBtn').addEventListener('click', async () => {
        try { await api('/api/admin/logout', { method: 'POST' }); } catch (_) {}
        sessionStorage.removeItem('admin_logged_in');
        if (refreshInterval) clearInterval(refreshInterval);
        adminShell.classList.add('hidden');
        loginShell.classList.remove('hidden');
        loginPassword.value = '';
        showToast('Signed out.', 'success');
      });

      // ── Retry button ─────────────────────────────────────────────────────
      document.getElementById('retryBtn').addEventListener('click', () => {
        hideError();
        loadAdminData(true);
      });

      // ── Prices ───────────────────────────────────────────────────────────
      // NOTE: /api/prices requires a regular user session (@login_required in app.py).
      // Admin has its own session (is_admin), so we fetch prices via the admin
      // investments list (which includes symbol data) and skip the live-price
      // endpoint gracefully — the ticker will just show "—" for prices unless
      // the server is extended.  We try anyway and degrade silently.
      async function fetchPrices() {
        try {
          const res = await api('/api/prices');
          if (!res.ok) return {};          // 401 from @login_required — degrade silently
          const data = await res.json();
          pricesCache = data.prices || {};
          return pricesCache;
        } catch (_) { return {}; }
      }

      // ── Load all data ─────────────────────────────────────────────────────
      async function loadAdminData(showLoading = true) {
        if (isLoading) return;
        isLoading = true;

        const tbody = document.getElementById('adminBody');
        const empty = document.getElementById('adminEmpty');

        try {
          if (showLoading) {
            tbody.innerHTML = '<tr class="loading-row"><td colspan="11">Loading investments…</td></tr>';
          }
          empty.classList.add('hidden');
          hideError();

          const res = await api('/api/admin/investments');

          if (res.status === 401) {
            // Admin session expired
            sessionExpired();
            return;
          }
          if (!res.ok) throw new Error(`Server error ${res.status}`);

          allInvestments = await res.json();

          // Try to get prices (may fail with 401 if no user session — that's OK)
          await fetchPrices();

          renderAdminTable(allInvestments, pricesCache);
          updateStats(allInvestments, pricesCache);
        } catch (err) {
          console.error('loadAdminData error:', err);
          tbody.innerHTML = `
            <tr class="error-row">
              <td colspan="11">
                ❌ ${escapeHtml(err.message)}
                <br><br>
                <button class="btn btn-sm btn-primary" onclick="window._retryLoad()">🔄 Retry</button>
              </td>
            </tr>`;
          showError(err.message || 'Failed to load data');
        } finally {
          isLoading = false;
        }
      }

      window._retryLoad = () => { hideError(); loadAdminData(true); };

      function sessionExpired() {
        showToast('Session expired — please log in again.', 'error');
        sessionStorage.removeItem('admin_logged_in');
        if (refreshInterval) clearInterval(refreshInterval);
        adminShell.classList.add('hidden');
        loginShell.classList.remove('hidden');
      }

      // ── Render table ──────────────────────────────────────────────────────
      function renderAdminTable(investments, prices) {
        const tbody = document.getElementById('adminBody');
        const empty = document.getElementById('adminEmpty');

        if (!investments || investments.length === 0) {
          tbody.innerHTML = '';
          empty.classList.remove('hidden');
          return;
        }
        empty.classList.add('hidden');

        tbody.innerHTML = investments.map(inv => {
          const priceInfo   = prices[inv.symbol] || {};
          const currentPrice = priceInfo.price ?? null;
          const costBasis   = inv.buy_price * inv.shares;
          const marketValue = currentPrice !== null ? currentPrice * inv.shares : costBasis;
          const gain        = currentPrice !== null ? marketValue - costBasis : null;
          const gainPct     = gain !== null && costBasis > 0 ? gain / costBasis * 100 : null;
          const gainColor   = gain !== null ? (gain >= 0 ? '#22c55e' : '#dc2626') : '';
          const gainStr     = gain !== null
            ? `$${gain >= 0 ? '+' : ''}${gain.toFixed(2)} (${gainPct >= 0 ? '+' : ''}${gainPct.toFixed(1)}%)`
            : '—';

          return `
            <tr data-id="${inv.id}">
              <td>${inv.id}</td>
              <td><span class="user-badge">${escapeHtml(inv.user_name)}</span></td>
              <td>${escapeHtml(inv.email || '—')}</td>
              <td><strong>${inv.symbol}</strong></td>
              <td>${inv.shares}</td>
              <td>$${inv.buy_price.toFixed(2)}</td>
              <td>$${costBasis.toFixed(2)}</td>
              <td>${currentPrice !== null ? '$' + currentPrice.toFixed(2) : '—'}</td>
              <td>$${marketValue.toFixed(2)}</td>
              <td style="color:${gainColor}">${gainStr}</td>
              <td>
                <div class="actions-cell">
                  <button class="btn-icon edit" onclick="window._edit(${inv.id})" title="Edit">
                    <svg viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                    Edit
                  </button>
                  <button class="btn-icon delete" onclick="window._delete(${inv.id})" title="Delete">
                    <svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    Delete
                  </button>
                  <button class="btn-icon create" onclick="window._copy(${inv.id})" title="Copy">
                    <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                    Copy
                  </button>
                </div>
              </td>
            </tr>`;
        }).join('');
      }

      // ── Stats ─────────────────────────────────────────────────────────────
      function updateStats(investments, prices) {
        let totalInvested = 0, totalValue = 0;
        const users = new Set();
        investments.forEach(inv => {
          users.add(inv.user_name);
          const cost = inv.buy_price * inv.shares;
          totalInvested += cost;
          const p = (prices[inv.symbol] || {}).price;
          totalValue += p !== null && p !== undefined ? p * inv.shares : cost;
        });
        document.getElementById('statTotalRows').textContent     = investments.length;
        document.getElementById('statTotalUsers').textContent    = users.size;
        document.getElementById('statTotalInvested').textContent = '$' + totalInvested.toFixed(2);
        document.getElementById('statTotalValue').textContent    = '$' + totalValue.toFixed(2);
      }

      // ── Ticker ────────────────────────────────────────────────────────────
      async function updateTicker() {
        const prices = await fetchPrices();
        const track  = document.getElementById('tickerTrack');
        const symbols = Object.keys(prices).length ? prices : null;
        if (!symbols) return;  // keep placeholder

        const items = Object.entries(prices).map(([sym, d]) => {
          const cls   = (d.change_pct ?? 0) >= 0 ? 'change-up' : 'change-down';
          const arrow = (d.change_pct ?? 0) >= 0 ? '▲' : '▼';
          return `<div class="ticker-item">
            <span class="sym">${sym}</span>
            ${d.price != null ? '$' + d.price.toFixed(2) : '—'}
            <span class="${cls}">${arrow} ${d.change_pct != null ? d.change_pct.toFixed(1) : '0.0'}%</span>
          </div>`;
        }).join('');
        track.innerHTML = items + items;   // duplicate for seamless scroll
      }

      // ── Modal helpers ─────────────────────────────────────────────────────
      const editOverlay   = document.getElementById('editModalOverlay');
      const editId        = document.getElementById('editId');
      const editUserName  = document.getElementById('editUserName');
      const editEmail     = document.getElementById('editEmail');
      const editSymbol    = document.getElementById('editSymbol');
      const editShares    = document.getElementById('editShares');
      const editBuyPrice  = document.getElementById('editBuyPrice');
      const modalTitleText = document.getElementById('modalTitleText');
      const modalSubmitBtn = document.getElementById('modalSubmitBtn');
      let currentMode = 'edit';

      function openModal(inv, mode) {
        currentMode = mode;
        modalTitleText.textContent = mode === 'create' ? 'Create New Investment' : 'Edit Investment';
        modalSubmitBtn.textContent = mode === 'create' ? 'Create' : 'Save Changes';
        editId.value       = inv.id ?? '';
        editUserName.value = inv.user_name ?? '';
        editEmail.value    = inv.email ?? '';
        editSymbol.value   = ALLOWED_SYMBOLS.includes(inv.symbol) ? inv.symbol : 'TSLA';
        editShares.value   = inv.shares ?? 1;
        editBuyPrice.value = inv.buy_price ?? 100;
        editOverlay.classList.remove('hidden');
        editUserName.focus();
      }

      window._edit = id => {
        const inv = allInvestments.find(i => i.id === id);
        inv ? openModal(inv, 'edit') : (showToast('Record not found — refresh first.', 'error'), loadAdminData());
      };

      window._delete = async id => {
        if (!confirm('Delete this investment?')) return;
        try {
          const res = await api(`/api/admin/investments/${id}`, { method: 'DELETE' });
          if (res.status === 401) { sessionExpired(); return; }
          if (!res.ok) { const e = await res.json(); throw new Error(e.error || 'Delete failed'); }
          showToast('Investment deleted.', 'success');
          loadAdminData(false);
          updateTicker();
        } catch (err) { showToast('❌ ' + err.message, 'error'); }
      };

      window._copy = id => {
        const inv = allInvestments.find(i => i.id === id);
        if (inv) openModal({ ...inv, id: null }, 'create');
      };

      document.getElementById('cancelEdit').addEventListener('click', () => editOverlay.classList.add('hidden'));
      editOverlay.addEventListener('click', e => { if (e.target === editOverlay) editOverlay.classList.add('hidden'); });

      // ── Save / Create ─────────────────────────────────────────────────────
      document.getElementById('editForm').addEventListener('submit', async e => {
        e.preventDefault();

        const symbol    = editSymbol.value;
        const shares    = parseFloat(editShares.value);
        const buy_price = parseFloat(editBuyPrice.value);

        if (!ALLOWED_SYMBOLS.includes(symbol)) { showToast('Symbol must be TSLA, AAPL, NVDA, or MSFT.', 'error'); return; }
        if (!shares || shares <= 0 || !buy_price || buy_price <= 0) { showToast('Enter valid shares and buy price.', 'error'); return; }

        const payload = {
          user_name: editUserName.value.trim(),
          email:     editEmail.value.trim(),
          symbol, shares, buy_price
        };

        const origText    = modalSubmitBtn.textContent;
        modalSubmitBtn.disabled    = true;
        modalSubmitBtn.textContent = 'Saving…';

        try {
          const isCreate = currentMode === 'create';
          const id       = parseInt(editId.value);
          const url      = isCreate ? '/api/admin/investments' : `/api/admin/investments/${id}`;
          const method   = isCreate ? 'POST' : 'PUT';

          if (!isCreate && (!id || isNaN(id))) { showToast('Invalid record ID.', 'error'); return; }

          const res = await api(url, { method, body: JSON.stringify(payload) });
          if (res.status === 401) { sessionExpired(); return; }

          const data = await res.json();
          if (!res.ok) throw new Error(data.error || 'Operation failed');

          editOverlay.classList.add('hidden');
          showToast(isCreate ? '✅ Investment created!' : '✅ Investment updated!', 'success');
          loadAdminData(false);
          updateTicker();
        } catch (err) {
          showToast('❌ ' + (err.message || 'Error saving.'), 'error');
        } finally {
          modalSubmitBtn.disabled    = false;
          modalSubmitBtn.textContent = origText;
        }
      });

      // ── Reset DB ──────────────────────────────────────────────────────────
      document.getElementById('resetDbBtn').addEventListener('click', async function () {
        if (!confirm('⚠️ This will DELETE ALL investment data. Are you sure?')) return;
        if (!confirm('⚠️ Final confirmation — this cannot be undone!')) return;
        this.disabled = true;
        this.textContent = 'Resetting…';
        try {
          const res  = await api('/api/admin/reset-db', { method: 'POST' });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || 'Reset failed');
          showToast('✅ Database reset!', 'success');
          loadAdminData(true);
        } catch (err) {
          showToast('❌ ' + err.message, 'error');
        } finally {
          this.disabled = false;
          this.textContent = 'Reset DB';
        }
      });

      // ── Toolbar buttons ───────────────────────────────────────────────────
      document.getElementById('createBtn').addEventListener('click', () =>
        openModal({ user_name:'', email:'', symbol:'TSLA', shares:1, buy_price:100 }, 'create')
      );

      document.getElementById('refreshBtn').addEventListener('click', () => {
        hideError();
        loadAdminData(true);
        updateTicker();
        showToast('Refreshed!', 'success');
      });

      // ── Helpers ───────────────────────────────────────────────────────────
      function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
      }

      // ── Check existing session on page load ───────────────────────────────
      async function checkSession() {
        try {
          const res  = await api('/api/admin/session');
          const data = await res.json();
          if (data.is_admin) {
            onLoginSuccess();
          } else {
            sessionStorage.removeItem('admin_logged_in');
          }
        } catch (_) {
          // Server not reachable — stay on login screen
          sessionStorage.removeItem('admin_logged_in');
        }
      }

      // Always verify with server — don't trust sessionStorage alone
      checkSession();

    })();
  </script>
</body>
</html>
