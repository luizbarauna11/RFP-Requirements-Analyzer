# Multi-stage com Red Hat UBI (padrão OpenShift). Usuário não-root (1001), porta > 1024.
FROM registry.access.redhat.com/ubi9/python-311:latest AS build
WORKDIR /opt/app-root/src
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /tmp/wheels ".[pdf,docx,obs]"

FROM registry.access.redhat.com/ubi9/python-311:latest
WORKDIR /opt/app-root/src
COPY --from=build /tmp/wheels /tmp/wheels
RUN pip install --no-cache-dir /tmp/wheels/*.whl && rm -rf /tmp/wheels
ENV APP_ENV=production \
    LLM_CACHE_DIR=/tmp/llm-cache \
    PYTHONUNBUFFERED=1
USER 1001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD curl -fs http://localhost:8080/health || exit 1
CMD ["uvicorn", "rfp_analyzer.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
