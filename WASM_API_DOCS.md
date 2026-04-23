# 3psLCCA WebAssembly API Documentation

This module provides an offline, browser-based execution engine for the 3psLCCA core using Pyodide. It allows frontend applications to run Life Cycle Cost Analysis without a backend server.

## 1. Installation

Include Pyodide and the engine wrapper in your frontend application:

\`\`\`html
<script src="https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js"></script>
<script src="path/to/lcca_wasm_api.js"></script>
\`\`\`

## 2. Initialization

Initialize the engine by passing the CDN link of the compiled `.whl` file.

\`\`\`javascript
const WHL_CDN_URL = "https://your-hosted-url.com/three_ps_lcca_core-0.0.0-py3-none-any.whl";
const lccaEngine = new LCCAEngine(WHL_CDN_URL);

// Must be awaited before calling calculations
await lccaEngine.init();
\`\`\`

## 3. Usage & Payload Structure

Once initialized, call the \`calculate()\` method and pass the required JSON payload.

### Expected Input Payload:
\`\`\`json
{
  "initial_construction_cost": 12843979.44,
  "initial_carbon_emissions_cost": 2065434.91,
  "superstructure_construction_cost": 9356038.92,
  "total_scrap_value": 2164095.02
}
\`\`\`

### Example Execution:
\`\`\`javascript
const payload = { /* ... */ };
const results = await lccaEngine.calculate(payload);
console.log(results.initial_stage.economic);
\`\`\`
