# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install dependencies into a specific directory to copy later
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy installed python packages from builder
COPY --from=builder /install /usr/local

# CRITICAL STEP:
# Your local folder structure is: backend/app/main.py
# We copy 'app' folder to '/app/app' inside the container.
COPY ./app ./app

# Expose port
EXPOSE 8000

# We run from /app (WORKDIR). 
# Uvicorn looks for folder "app", file "main.py", object "app".
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
