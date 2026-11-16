import fs from 'fs';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const wasmPath = path.join(__dirname, 'deepseek.wasm');

const wasmBytes = fs.readFileSync(wasmPath);

let wasmInstance, wasmExports, memory, malloc, stack_ptr;

async function init() {
    const { instance } = await WebAssembly.instantiate(wasmBytes, {});
    wasmInstance = instance;
    wasmExports = instance.exports;
    memory = wasmExports.memory;
    malloc = wasmExports.__wbindgen_export_0;
    stack_ptr = wasmExports.__wbindgen_add_to_stack_pointer(-16);
}

function allocUtf8(str) {
    const encoder = new TextEncoder();
    const bytes = encoder.encode(str);
    const ptr = malloc(bytes.length, 1);
    const view = new Uint8Array(memory.buffer, ptr, bytes.length);
    view.set(bytes);
    return [ptr, bytes.length];
}

async function solvePow(challenge, salt, expireAt, difficulty) {
    await init();
    const prefix = `${salt}_${expireAt}_`;

    const [challengePtr, challengeLen] = allocUtf8(challenge);
    const [prefixPtr, prefixLen] = allocUtf8(prefix);

    wasmExports.wasm_solve(stack_ptr, challengePtr, challengeLen,
                          prefixPtr, prefixLen, difficulty);

    const view = new DataView(memory.buffer, stack_ptr, 16);
    const found = view.getInt32(0, true);
    const answer = view.getFloat64(8, true);

    if (found === 0) throw new Error("POW not found");
    return Math.floor(answer);
}

// Read JSON from stdin: { algorithm, challenge, salt, expire_at, difficulty, signature, target_path }
let input = '';
process.stdin.setEncoding('utf-8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', async () => {
    const data = JSON.parse(input);
    try {
        const answer = await solvePow(data.challenge, data.salt,
                                      data.expire_at, data.difficulty);
        console.log(answer.toString());
    } catch (e) {
        console.error(e.message);
        process.exit(1);
    }
});
