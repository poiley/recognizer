FROM oven/bun:1.0.35-slim
WORKDIR /app

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
EXPOSE $PORT

# Start the server with host binding
CMD ["bun", "run", "preview", "--host", "0.0.0.0", "--port", "$FRONTEND_PORT"]
