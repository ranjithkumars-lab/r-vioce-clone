# syntax=docker/dockerfile:1

# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve via Nginx
FROM nginx:alpine

# Create a non-root user (nginx image usually runs as root)
# Let's just adjust the default nginx user and configure it to run unprivileged if possible.
# A simpler approach for standard nginx is to copy our conf and chown the necessary dirs.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build output
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
