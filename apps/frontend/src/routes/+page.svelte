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
  let allCompanies: Company[] = [];
  let loading = true;
  let error = "";
  let nlpQuery = "";
  let parsedFilter = "";
  let queryLoading = false;

  async function loadCompanies() {
    try {
      const res = await fetch("http://localhost:8000/api/companies");
      const data = await res.json();
      companies = data.companies;
      allCompanies = data.companies;
      loading = false;
    } catch (err) {
      error = "Failed to load companies from backend";
      loading = false;
    }
  }

  async function executeNLPQuery() {
    if (!nlpQuery.trim()) {
      companies = allCompanies;
      parsedFilter = "";
      error = "";
      return;
    }

    queryLoading = true;
    error = "";
    try {
      const res = await fetch("http://localhost:8000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: nlpQuery, collection: "companies" })
      });
      const data = await res.json();
      
      if (data.error) {
        error = data.error;
        parsedFilter = "";
        companies = allCompanies;
      } else if (data.query_type === "aggregation") {
        // Handle aggregation result
        const agg = data.aggregation_result;
        parsedFilter = `${agg.operation.toUpperCase()}(${agg.field || 'all'}): ${agg.value.toLocaleString()}`;
        companies = allCompanies; // Show all data with aggregation result
        error = "";
      } else {
        companies = data.results;
        parsedFilter = JSON.stringify(data.parsed_filter, null, 2);
        if (data.count === 0) {
          error = "No results found matching your query";
        }
      }
    } catch (err) {
      error = "Failed to execute query";
      parsedFilter = "";
    }
    queryLoading = false;
  }

  function resetQuery() {
    nlpQuery = "";
    parsedFilter = "";
    error = "";
    companies = allCompanies;
  }

  loadCompanies();
</script>

<main>
  <div class="container">
    <h1>MongoDB Company Dashboard</h1>
    
    {#if loading}
      <div class="loading">Loading companies...</div>
    {:else}
      <div class="query-section">
        <input 
          type="text" 
          bind:value={nlpQuery} 
          placeholder="Try: 'total employees' or 'count companies' or 'revenue greater than 5 million'"
          on:keydown={(e) => e.key === 'Enter' && executeNLPQuery()}
        />
        <button on:click={executeNLPQuery} disabled={queryLoading}>
          {queryLoading ? 'Searching...' : 'Search'}
        </button>
        <button on:click={resetQuery}>Reset</button>
        {#if error}
          <div class="error-message">{error}</div>
        {/if}
        {#if parsedFilter}
          <div class="filter-info">Filter: {parsedFilter}</div>
        {/if}
      </div>
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

  .query-section {
    margin-bottom: 1rem;
    padding: 1rem;
    border: 1px solid #000;
  }

  .query-section input {
    width: 70%;
    padding: 0.5rem;
    border: 1px solid #000;
    font-size: 0.875rem;
  }

  .query-section button {
    padding: 0.5rem 1rem;
    border: 1px solid #000;
    background: #fff;
    cursor: pointer;
    margin-left: 0.5rem;
  }

  .query-section button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .filter-info {
    margin-top: 0.5rem;
    padding: 0.5rem;
    border: 1px solid #000;
    background: #f9f9f9;
    font-size: 0.75rem;
   error-message {
    margin-top: 0.5rem;
    padding: 0.5rem;
    border: 1px solid #000;
    background: #fff;
    font-size: 0.875rem;
    color: #000;
  }

  . font-family: monospace;
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

