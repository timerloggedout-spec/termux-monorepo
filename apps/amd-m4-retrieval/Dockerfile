# AMD AI League M4 — container per league contract (packet of record: PR #2543).
# Multi-stage; FINAL stage starts from the mandated ROCm base image; no squash.
# syntax=docker/dockerfile:1

# ---- stage 1: dependencies into a venv, on the mandated base (py3.14 => final-stage match)
FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0 AS deps
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# ---- stage 2 (FINAL): mandated ROCm base; app at /app; runs as-is
FROM rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=deps /opt/venv /opt/venv
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt
# /models is optional per contract — none shipped at P0 (CPU-only pipeline).
EXPOSE 8080
CMD ["python3", "/app/app.py", "--serve", "--port", "8080"]
