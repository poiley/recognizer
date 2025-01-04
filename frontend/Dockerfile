FROM oven/bun:1.0.35-slim
WORKDIR /app

# Copy package files
COPY package*.json .

# Install dependencies with Bun
RUN bun install

# Copy source code
COPY . .

# Build the application
RUN bun run build

# Expose the port
EXPOSE 5173

# Start the server with host binding on port 5173
CMD ["bun", "run", "preview", "--host", "0.0.0.0", "--port", "5173"]
