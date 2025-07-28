# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose default Dash port
EXPOSE 8050

# Start the Dash app
CMD ["python", "app.py"]
