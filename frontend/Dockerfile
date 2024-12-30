FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the remaining application files
COPY . .

# Ensure a clean rebuild
RUN rm -rf node_modules package-lock.json && npm install

# Build the project
RUN npm run build

# Expose the development port
EXPOSE 5173

# Start the development server
CMD ["npm", "run", "dev", "--", "--host"]
