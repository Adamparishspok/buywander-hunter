FROM node:22-alpine

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy package files
COPY package.json ./

# Install dependencies (no frozen lockfile since it's in root)
RUN pnpm install

# Copy source
COPY . .

# Build
RUN pnpm run build

# Start
EXPOSE 3001
CMD ["pnpm", "start"]
