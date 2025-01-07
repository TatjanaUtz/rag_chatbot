#!/bin/sh

# Function to replace placeholders in config.js with environment variables or default values
replace_placeholder() {
    local placeholder=$1
    local value=$2
    sed -i "s|$placeholder|${value:-$placeholder}|g" /usr/share/nginx/html/config.js
}

# Replace placeholders with actual environment variables or default values
replace_placeholder "UI_BACKEND_URL" "${UI_BACKEND_URL}"
replace_placeholder "UI_TITLE" "${UI_TITLE}"
replace_placeholder "UI_HEADER" "${UI_HEADER}"
replace_placeholder "UI_WELCOME_MESSAGE" "${UI_WELCOME_MESSAGE}"

# Log the replacement success
echo "Placeholders in config.js have been replaced with environment variables or default values."

# Start nginx
echo "Starting Nginx..."
nginx -g 'daemon off;'
