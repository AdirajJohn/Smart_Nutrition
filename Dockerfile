# Stage 1: Build React frontend
FROM node:18 AS frontend-builder

WORKDIR /app/frontend
COPY frontend/ ./
RUN npm install && npm run build

# Stage 2: Build FastAPI backend
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && apt-get clean

# Set working directory
WORKDIR /app

# Copy Python backend files
COPY main.py ./
COPY requirements.txt ./
# Copy the backend logic folder
COPY backend/ ./backend/
COPY data/ ./data/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the React frontend build folder
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]