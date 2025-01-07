# Use the official Nginx image from the Docker Hub
FROM nginx:alpine

# Copy the content of the current directory to the Nginx HTML directory and the entrypoint script
COPY . /usr/share/nginx/html
COPY entrypoint.sh /entrypoint.sh

# Set permissions and make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose port 80 to the outside world
EXPOSE 80

# Add a health check to monitor the Nginx service
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
