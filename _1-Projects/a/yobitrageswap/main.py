import sys

try:
    from .strategies.engine import run_all
    from .api.uniswap_api import UniswapAPI
    from .api.yobit_api import YobitAPI
    from .api.polygon_api import PolygonAPI
    from .api.indodax_api import IndodaxAPI
    from .api.tastytrade_api import TastytradeAPI
    from .api.solana_api import SolanaAPI
    from .api.pumpfun_api import PumpfunAPI

    _apis = []
    for cls in [UniswapAPI, YobitAPI, PolygonAPI, IndodaxAPI, TastytradeAPI, SolanaAPI, PumpfunAPI]:
        try:
            _apis.append(cls())
        except Exception as e:
            print(f"[engine] failed to init {cls.__name__}: {e}", file=sys.stderr)

    _res = run_all(_apis)
    top = {k: {'bid': (v['bids'][0][0] if v['bids'] else None),
               'ask': (v['asks'][0][0] if v['asks'] else None)} for k, v in _res['books'].items()}
    print("[engine] top-of-book:", top)
    print("[compute] summary:", _res['compute'])
except Exception as e:
    print("[engine] init error:", e, file=sys.stderr)
