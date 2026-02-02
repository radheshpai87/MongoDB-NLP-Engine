<script lang="ts">
  interface User {
    _id: string;
    name: string;
    email: string;
    role: string;
    status: string;
    joined: string;
  }

  let users: User[] = [];
  let loading = true;
  let error = "";

  async function loadUsers() {
    try {
      const res = await fetch("http://localhost:8000/api/users");
      const data = await res.json();
      users = data.users;
      loading = false;
    } catch (err) {
      error = "Failed to load users from backend";
      loading = false;
    }
  }

  loadUsers();
</script>

<main>
  <div class="container">
    <h1>🚀 MongoDB User Dashboard</h1>
    
    {#if loading}
      <div class="loading">Loading users...</div>
    {:else if error}
      <div class="error">{error}</div>
    {:else}
      <div class="stats">
        <div class="stat-card">
          <div class="stat-number">{users.length}</div>
          <div class="stat-label">Total Users</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{users.filter(u => u.status === 'Active').length}</div>
          <div class="stat-label">Active Users</div>
        </div>
      </div>

      <div class="users-grid">
        {#each users as user}
          <div class="user-card">
            <div class="user-header">
              <div class="user-avatar">{user.name.split(' ').map(n => n[0]).join('')}</div>
              <div class="user-info">
                <h3>{user.name}</h3>
                <p class="email">{user.email}</p>
              </div>
            </div>
            <div class="user-details">
              <div class="detail-item">
                <span class="label">Role:</span>
                <span class="value">{user.role}</span>
              </div>
              <div class="detail-item">
                <span class="label">Status:</span>
                <span class="status-badge status-{user.status.toLowerCase()}">{user.status}</span>
              </div>
              <div class="detail-item">
                <span class="label">Joined:</span>
                <span class="value">{new Date(user.joined).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    min-height: 100vh;
  }

  main {
    padding: 2rem;
    min-height: 100vh;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
  }

  h1 {
    color: white;
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
  }

  .loading, .error {
    text-align: center;
    color: white;
    font-size: 1.2rem;
    padding: 2rem;
  }

  .error {
    background: rgba(255, 0, 0, 0.2);
    border-radius: 8px;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
  }

  .stat-number {
    font-size: 3rem;
    font-weight: bold;
    color: #667eea;
  }

  .stat-label {
    color: #666;
    font-size: 1rem;
    margin-top: 0.5rem;
  }

  .users-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }

  .user-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .user-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 12px rgba(0,0,0,0.15);
  }

  .user-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #eee;
  }

  .user-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
  }

  .user-info h3 {
    margin: 0;
    color: #333;
    font-size: 1.2rem;
  }

  .email {
    margin: 0.25rem 0 0;
    color: #666;
    font-size: 0.9rem;
  }

  .user-details {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .label {
    color: #666;
    font-size: 0.9rem;
    font-weight: 500;
  }

  .value {
    color: #333;
    font-weight: 500;
  }

  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .status-active {
    background: #d4edda;
    color: #155724;
  }

  .status-away {
    background: #fff3cd;
    color: #856404;
  }
</style>

