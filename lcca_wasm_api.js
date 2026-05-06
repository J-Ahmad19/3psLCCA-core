/**
 * 3psLCCA WebAssembly Engine API
 */
class LCCAEngine {
    constructor(whlUrl) {
        this.whlUrl = whlUrl; 
        this.pyodide = null;
        this.isReady = false;
    }

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

    // Now it ONLY requires the costData from the frontend
    async calculate(costData) {
        if (!this.isReady) {
            throw new Error("Engine is not initialized. Call init() first.");
        }

        window.__lcca_cost_payload = costData;

        const resultString = await this.pyodide.runPythonAsync(`
import json
import js
from three_ps_lcca_core.core.main import run_full_lcc_analysis, get_IRC_standard_suggestions

# 1. Import the default configurations directly from the package
from examples.from_dict.Input import Input
from examples.from_dict.wpi import wpi

# 2. Pull only the dynamic construction costs from the frontend
cost_dict = js.window.__lcca_cost_payload.to_py()

# 3. Run the analysis combining the frontend costs and internal defaults
analysis_results = run_full_lcc_analysis(
    Input, 
    cost_dict,  
    wpi=wpi, 
    debug=False
)

suggestions = get_IRC_standard_suggestions()

full_response = {
    "analysis_results": analysis_results,
    "irc_suggestions": suggestions
}

json.dumps(full_response)
        `);

        delete window.__lcca_cost_payload;

        return JSON.parse(resultString);
    }
}