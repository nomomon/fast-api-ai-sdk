# Due to monorepo structure, this assumes 
# the Docker context is the ROOT of your repo, 
# not the frontend/ folder.


FROM node:20-alpine AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# ---------------------------------------------------------
# Stage 1: Pruner
# Isolate this specific app from the monorepo
# ---------------------------------------------------------
FROM base AS pruner
RUN apk add --no-cache libc6-compat
WORKDIR /app
RUN npm install -g turbo
COPY . .
# Generates a pruned "out" directory with only necessary files
# "fast-api-ai-sdk-frontend" must match name in frontend/package.json
RUN turbo prune fast-api-ai-sdk-frontend --docker

# ---------------------------------------------------------
# Stage 2: Builder
# Install deps and build the app
# ---------------------------------------------------------
FROM base AS builder
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy lockfile and package.json's first (for better caching)
COPY --from=pruner /app/out/json/ .
COPY --from=pruner /app/out/pnpm-lock.yaml ./pnpm-lock.yaml
# We still want turbo.json explicitly
COPY --from=pruner /app/turbo.json ./turbo.json

# Install dependencies
RUN pnpm install --frozen-lockfile --ignore-scripts

# Copy the full source code for the specific app
COPY --from=pruner /app/out/full/ .

# Build the project
ENV NEXT_TELEMETRY_DISABLED 1
# Note: Next.js requires build-time env vars. If your build crashes 
# due to missing keys, you may need to add dummy ARG vars here.
RUN pnpm run build

# ---------------------------------------------------------
# Stage 3: Runner
# Production image
# ---------------------------------------------------------
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# In a monorepo, the standalone output preserves folder structure
# Copy public assets
COPY --from=builder /app/frontend/public ./frontend/public

# Copy the standalone server and static files
# The path is frontend/.next because we built from root context
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/static ./frontend/.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOST=0.0.0.0

# Start the server (path includes workspace folder)
CMD ["node", "frontend/server.js"]
