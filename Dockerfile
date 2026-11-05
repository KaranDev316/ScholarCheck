FROM node:24-bookworm-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim
WORKDIR /srv/backend
COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN pip install --no-cache-dir .
COPY content /srv/content
COPY --from=frontend /build/dist /srv/frontend/dist
ENV APP_ENV=production FRONTEND_DIST=/srv/frontend/dist
RUN useradd --create-home scholarcheck && mkdir -p /srv/backend/var && chown scholarcheck /srv/backend/var
USER scholarcheck
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers"]
