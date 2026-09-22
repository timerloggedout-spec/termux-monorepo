# Laya deployment lanes

GitHub Actions is the canonical automated live smoke and CADENCE sweep lane. It pins Laya 0.3.5, uses Python 3.12, disables TensorFlow probing, caches Hugging Face weights, and publishes receipts.

Render is the long-lived HTTP adapter lane and requires enough memory for the selected checkpoint.

Colab is the GPU/large-memory benchmark lane: install laya 0.3.5 and run USE_TF=0 python scripts/laya_sweep.py --live.

Hugging Face supplies the upstream weights used by the pinned package.

Vercel should host observation/control UI or a proxy, not model residency.

The GitHub laya-live environment is the place for optional deployment credentials. Secret values never belong in the repository.
