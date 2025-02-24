# Use a lightweight base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install -U --no-cache-dir pip && \
    pip install -U --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port for Gradio
EXPOSE 7860

# Set the command to run the application
CMD ["python", "src/main.py"]

# Add a health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:7860/config || exit 1
