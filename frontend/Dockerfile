FROM node:20-alpine
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install -g npm@latest
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Clean dev environment
RUN rm -rf node_modules
RUN npm install

# Runtime config
ENV HOST=0.0.0.0
EXPOSE 5173

# Start dev server
CMD ["npm", "run", "dev", "--", "--host"]
