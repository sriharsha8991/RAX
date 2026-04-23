# RAX Frontend — Vite dev server (hot-reload friendly for local Docker dev)
FROM node:20-alpine

WORKDIR /app

# Install deps first for layer cache
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
COPY . .

EXPOSE 5173

# --host 0.0.0.0 so the port is reachable from outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
