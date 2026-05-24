# slim python = parent image
FROM python:3.11-slim

# python - environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# set the working directory = /app
WORKDIR /app

# copy dependency definitions 
COPY requirements-api.txt .

# install required dependencies, then python packages
RUN pip install --no-cache-dir -r requirements-api.txt

# copy the entire api directory into the container
COPY api/ ./api/

# expose the default Cloud Run port
EXPOSE 8080

# run uvicorn pointing to the app inside the api package
# Cloud Run injects the PORT env var automatically ${PORT}
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"] 