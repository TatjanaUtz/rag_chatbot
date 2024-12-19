# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/app"

# Copy the current directory contents into the container at /app
COPY . /app/indexing

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r indexing/requirements.txt

# Run the directory monitor script when the container launches
CMD ["python", "indexing/main.py"]
