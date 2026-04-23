

/**
 * 3psLCCA WebAssembly Engine API
 * This script initializes the Python engine and exposes the calculation function.
 */

class LCCAEngine {
    constructor(whlUrl) {
        this.whlUrl = whlUrl; // The URL to the .whl file (will act as the CDN)
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

    // 2. The main API function to be called by the frontend
    async calculate(jsonPayload) {
        if (!this.isReady) {
            throw new Error("Engine is not initialized. Call init() first.");
        }

        // Convert the JS object payload into a JSON string for Python
        const payloadString = JSON.stringify(jsonPayload);

        // Run the Python calculation
        const resultString = await this.pyodide.runPythonAsync(`
            import json
            from three_ps_lcca_core.core.main import run_full_lcc_analysis
            from examples.from_dict.Input import Input
            from examples.from_dict.wpi import wpi

            # Load the payload sent from the frontend
            payload = json.loads('${payloadString}')

            # Run analysis using the dynamic payload
            results = run_full_lcc_analysis(
                Input, 
                payload,  # Passing the payload exactly as received
                wpi=wpi, 
                debug=False
            )

            # Return as JSON string
            json.dumps(results)
        `);

        // Parse it back to a JS object and return it to the frontend
        return JSON.parse(resultString);
    }
}
