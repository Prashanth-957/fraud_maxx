# Use Python 3.11 slim image
FROM python:3.11.8-slim

# Set the working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (ignoring warnings for clean build)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code and Procfile to the container
COPY backend/ ./backend/
COPY Procfile .

# Expose port (8080 is common for Docker, but Railway overrides it dynamically)
ENV PORT=8080
EXPOSE $PORT

# Run the app using Gunicorn directly from the backend folder
CMD ["sh", "-c", "cd backend && gunicorn --bind 0.0.0.0:${PORT} api:app"]
