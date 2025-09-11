# Use a minimal, official Python image
##### Builder stage: install dependencies #####
FROM python:3.10-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /install

# Install build tools for compiling wheels
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential gcc \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /install/requirements.txt

# Install into a prefix so we can copy into the final image
RUN python -m pip install --upgrade pip \
	&& pip install --no-cache-dir --prefix=/install -r /install/requirements.txt


##### Final stage: runtime only, no build tools #####
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application files
COPY . /app

# Default command
CMD ["python"]