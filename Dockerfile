# Use an official lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyPDF2 and ReportLab if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy your app code to the image
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5000

# Run the app
CMD ["python", "webApp.py"]