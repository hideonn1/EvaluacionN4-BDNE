FROM python:3.11-slim
WORKDIR /workspace
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /workspace
USER appuser
#----------------------
CMD ["python", "src/main.py"]
