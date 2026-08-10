
const fs = require('fs');
const path = require('path');
const wasmPath = process.argv[2];
const wasm = fs.readFileSync(wasmPath);
WebAssembly.instantiate(wasm).then(obj => {
    // Assume the module exports a 'solve' function
    const result = obj.instance.exports.solve();
    console.log(JSON.stringify({ answer: result.answer, signature: result.signature }));
});
