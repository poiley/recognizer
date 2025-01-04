FROM oven/bun:1.0.35-slim
WORKDIR /app

# Version from build arg
ARG VERSION
LABEL version=$VERSION

# Copy package files
COPY package*.json .

# Install dependencies with Bun
RUN bun install

# Copy source code
COPY . .

# Build the application
RUN bun run build

# Expose the port
EXPOSE $FRONTEND_PORT

# Start the server with host binding
CMD ["sh", "-c", "bun run preview --host 0.0.0.0 --port $FRONTEND_PORT"]
