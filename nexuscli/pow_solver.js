// POW Solver for DeepSeek API
// Used by deepcode-cli to solve Proof-of-Work challenges

const crypto = require('crypto');

function solveDeepSeekHashV1(challenge, salt, signature, targetPath) {
    const target = targetPath || '/api/v0/chat/completion';
    let answer = 0;
    const prefix = crypto.createHash('sha256')
        .update(challenge + target + salt + signature)
        .digest('hex')
        .substring(0, 16);
    
    while (true) {
        const input = prefix + answer.toString();
        const hash = crypto.createHash('sha256').update(input).digest('hex');
        if (hash.startsWith('000000')) {
            return answer;
        }
        answer++;
    }
}

const input = JSON.parse(require('fs').readFileSync(0, 'utf-8').trim());
const challenge = input.challenge;
const salt = input.salt;
const signature = input.signature;
const targetPath = input.target_path || '/api/v0/chat/completion';
const algorithm = input.algorithm || 'DeepSeekHashV1';

let answer;
if (algorithm === 'DeepSeekHashV1') {
    answer = solveDeepSeekHashV1(challenge, salt, signature, targetPath);
} else {
    // Fallback for other algorithms
    answer = 0;
    const prefix = crypto.createHash('sha256')
        .update(challenge + targetPath + salt + signature)
        .digest('hex')
        .substring(0, 16);
    
    while (true) {
        const inputStr = prefix + answer.toString();
        const hash = crypto.createHash('sha256').update(inputStr).digest('hex');
        if (hash.startsWith('000000')) {
            break;
        }
        answer++;
    }
}

console.log(answer);
