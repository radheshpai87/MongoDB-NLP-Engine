<script lang="ts">
  interface Company {
    _id: string;
    name: string;
    industry: string;
    revenue: number;
    employees: number;
    founded: string;
    status: string;
  }

  let companies: Company[] = [];
  let loading = true;
  let error = "";

  async function loadCompanies() {
    try {
      const res = await fetch("http://localhost:8000/api/companies");
      const data = await res.json();
      companies = data.companies;
      loading = false;
    } catch (err) {
      error = "Failed to load companies from backend";
      loading = false;
    }
  }

  loadCompanies();
</script>

<main>
  <div class="container">
    <h1>MongoDB Company Dashboard</h1>
    
    {#if loading}
      <div class="loading">Loading companies...</div>
    {:else if error}
      <div class="error">{error}</div>
    {:else}
      <div class="stats">
        <div class="stat-card">
          <div class="stat-number">{companies.length}</div>
          <div class="stat-label">Total Companies</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{companies.reduce((sum, c) => sum + c.employees, 0)}</div>
          <div class="stat-label">Total Employees</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">${(companies.reduce((sum, c) => sum + c.revenue, 0) / 1000000).toFixed(1)}M</div>
          <div class="stat-label">Total Revenue</div>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Company Name</th>
            <th>Industry</th>
            <th>Revenue</th>
            <th>Employees</th>
            <th>Founded</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {#each companies as company}
            <tr>
              <td>{company.name}</td>
              <td>{company.industry}</td>
              <td>${(company.revenue / 1000000).toFixed(2)}M</td>
              <td>{company.employees}</td>
              <td>{new Date(company.founded).toLocaleDateString()}</td>
              <td>{company.status}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    background: #fff;
    font-family: Arial, sans-serif;
    min-height: 100vh;
  }

  main {
    padding: 1rem;
  }

  .container {
    max-width: 1400px;
    margin: 0 auto;
  }

  h1 {
    color: #000;
    font-size: 1.5rem;
    margin-bottom: 1rem;
    font-weight: normal;
  }

  .loading, .error {
    padding: 1rem;
  }

  .error {
    border: 1px solid #000;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .stat-card {
    border: 1px solid #000;
    padding: 1rem;
  }

  .stat-number {
    font-size: 2rem;
    font-weight: bold;
  }

  .stat-label {
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #000;
  }

  th, td {
    border: 1px solid #000;
    padding: 0.75rem;
    text-align: left;
  }

  th {
    background: #f0f0f0;
    font-weight: bold;
  }

  tbody tr:nth-child(even) {
    background: #fafafa;
  }
</style>

