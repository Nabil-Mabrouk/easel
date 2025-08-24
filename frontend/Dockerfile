# Stage 1: Build the Vue.js application
FROM node:20-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application files
COPY . .

# Build the application for production
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:stable-alpine

# Copy the built files from the 'build' stage to the Nginx public directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy the default Nginx configuration. This is often sufficient for Vite apps.
# You could also copy a custom nginx.conf file here if needed.
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]