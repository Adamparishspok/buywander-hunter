FROM node:22-alpine

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy workspace root files for pnpm workspace resolution
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy auth-server package.json
COPY auth-server/package.json ./auth-server/

# Copy frontend package.json (needed for workspace install)
COPY frontend/package.json ./frontend/

# Install dependencies using workspace lockfile
RUN pnpm install --frozen-lockfile --filter auth-server

WORKDIR /app/auth-server

# Copy auth-server source
COPY auth-server/ .

# Build TypeScript
RUN pnpm run build

# Start
EXPOSE 3001
CMD ["pnpm", "start"]
