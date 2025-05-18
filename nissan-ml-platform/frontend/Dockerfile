FROM node:18-alpine

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the application code
COPY . ./

# Verify public directory contents
RUN ls -la public/ || echo "public directory is empty or missing"

# Build the application for production
RUN npm run build

# Install serve for running the built app
RUN npm install -g serve

# Expose the port
EXPOSE 3000

# Command to serve the app
CMD ["serve", "-s", "build", "-l", "3000"]