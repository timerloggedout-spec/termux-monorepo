FROM python:3.12-slim
WORKDIR /app
ENV AWS_EC2_METADATA_DISABLED=true
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py agent.py study_tools.py VERSION ./
COPY foundation/ ./foundation/
COPY examples/ ./examples/
CMD ["python", "app.py"]
