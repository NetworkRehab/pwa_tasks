# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install testing dependencies
RUN pip install --no-cache-dir pytest

# Create the data directory
RUN mkdir -p /app/data

# Declare the volume
VOLUME ["/app/data"]

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

EXPOSE 5000