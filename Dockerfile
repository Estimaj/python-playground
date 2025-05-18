# Dockerfile

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    build-essential \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy requirements if you have them
COPY requirements.txt .
RUN pip install -r requirements.txt

# Optional: copy your code
COPY . .

CMD [ "bash" ]