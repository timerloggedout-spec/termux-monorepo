from . import deploy, evaluate, features, ingest, monitor, recon, train

STAGES = [
    ("00_recon", recon.run),
    ("10_ingest", ingest.run),
    ("20_features", features.run),
    ("30_train", train.run),
    ("40_evaluate", evaluate.run),
    ("50_deploy", deploy.run),
    ("60_monitor", monitor.run),
]
