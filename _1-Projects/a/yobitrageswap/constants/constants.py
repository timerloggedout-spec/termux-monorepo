SWAP_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "bytes", "name": "path", "type": "bytes"},
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"}
        ],
        "name": "exactInput",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

TOKEN_ADDRESSES = {
    'weth': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    'uni': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
    'dai': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    'usdc': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'usdt': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'link': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
    'aave': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
    'comp': '0xc00e94Cb662C3520282E6f5717214004A7f26888',
    'snx': '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F',
    'yfi': '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e',
    'crv': '0xD533a949740bb3306d119CC777fa900bA034cd52',
    'sushi': '0x6B3595068778DD592e39A122f4f5a5cF09C90fE2',
    '1inch': '0x111111111117dC0aa78b770fA6A738034120C302',
    'mkr': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
    'zrx': '0xE41d2489571d322189246DaFA5ebDe1F4699F498'
}
