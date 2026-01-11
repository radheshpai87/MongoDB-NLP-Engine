<script lang="ts">
  let message = "Loading...";

  async function loadBackend() {
    try {
      const res = await fetch("http://localhost:8000/health");
      const data = await res.json();
      message = data.message;
    } catch (err) {
      message = "Failed to reach backend";
    }
  }

  loadBackend();
</script>

<main style="padding: 2rem; font-family: sans-serif;">
  <h1>Docker Test</h1>
  <p>Backend says: <strong>{message}</strong></p>
</main>
