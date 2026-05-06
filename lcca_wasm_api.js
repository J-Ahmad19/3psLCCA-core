/**
 * 3psLCCA WebAssembly Engine API
 * This script initializes the Python engine and exposes the calculation function.
 */

class LCCAEngine {
    constructor(whlUrl) {
        this.whlUrl = whlUrl; // The CDN URL to the .whl file
        this.pyodide = null;
        this.isReady = false;
    }

    // 1. Initialize the engine
    async init() {
        if (this.isReady) return;
        
        console.log("Initializing Pyodide...");
        this.pyodide = await window.loadPyodide();
        
        console.log("Installing micropip...");
        await this.pyodide.loadPackage("micropip");
        const micropip = this.pyodide.pyimport("micropip");
        
        console.log(`Fetching 3psLCCA wheel from: ${this.whlUrl}`);
        await micropip.install(this.whlUrl);
        
        this.isReady = true;
        console.log("LCCA Engine Ready!");
    }

    /**
     * 2. The main API function to be called by the frontend
     * @param {Object} inputData - Matches InputMetaData structure (Traffic, Service Life, etc.)
     * @param {Object} costData - Construction cost breakdown (User input)
     * @param {Object} wpiData - Matches WPIMetaData structure
     */
    async calculate(inputData, costData, wpiData) {
        if (!this.isReady) {
            throw new Error("Engine is not initialized. Call init() first.");
        }

        // Attach the JS objects to the global window so Python can read them securely without string interpolation
        window.__lcca_payloads = {
            input: inputData,
            cost: costData,
            wpi: wpiData
        };

        const resultString = await this.pyodide.runPythonAsync(`
import json
import js
from three_ps_lcca_core.core.main import run_full_lcc_analysis, get_IRC_standard_suggestions

# Safely pull the JavaScript objects into Python dictionaries
js_payloads = js.window.__lcca_payloads

input_dict = js_payloads.input.to_py()
cost_dict = js_payloads.cost.to_py()
wpi_dict = js_payloads.wpi.to_py()

# Run the full analysis using the dynamic dictionaries from the frontend
analysis_results = run_full_lcc_analysis(
    input_dict, 
    cost_dict,  
    wpi=wpi_dict, 
    debug=False
)

# Fetch the IRC suggestions
suggestions = get_IRC_standard_suggestions()

# Merge them into one object
full_response = {
    "analysis_results": analysis_results,
    "irc_suggestions": suggestions
}

json.dumps(full_response)
        `);

        // Clean up the global window object to prevent memory leaks
        delete window.__lcca_payloads;

        // Parse it back to a JS object and return it to the frontend
        return JSON.parse(resultString);
    }
}