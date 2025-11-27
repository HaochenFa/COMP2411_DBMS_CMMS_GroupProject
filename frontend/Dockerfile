FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build the production bundle
COPY . .
RUN npm run build

EXPOSE 5173

# Serve the built app using Vite's preview server
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"]
