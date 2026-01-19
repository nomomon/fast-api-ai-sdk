# Due to monorepo structure, this assumes 
# the Docker context is the ROOT of your repo, 
# not the frontend/ folder.


FROM node:20-alpine AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

FROM base AS pruner
RUN apk add --no-cache libc6-compat
WORKDIR /app
RUN npm install -g turbo
COPY . .
RUN turbo prune fast-api-ai-sdk-frontend --docker

FROM base AS builder
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY --from=pruner /app/out/json/ .
COPY --from=pruner /app/out/pnpm-lock.yaml ./pnpm-lock.yaml
COPY --from=pruner /app/turbo.json ./turbo.json

RUN pnpm install --frozen-lockfile --ignore-scripts

COPY --from=pruner /app/out/full/ .


RUN pnpm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/frontend/public ./frontend/public
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/static ./frontend/.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOST=0.0.0.0

CMD ["node", "frontend/server.js"]
