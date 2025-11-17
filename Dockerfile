# Use an official Node.js image as the base
FROM node:16-slim

# Install Python and required dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# Install Python dependencies directly
RUN pip3 install cloudscraper requests beautifulsoup4 googletrans==4.0.0rc1

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Node.js dependencies
RUN npm install

# Expose port for communication (if needed)
EXPOSE 8080

# Command to start the Node.js bot
CMD ["node", "bot.js"]
