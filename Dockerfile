FROM ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 AS uv

FROM python:3.12-slim-trixie@sha256:b18b261e1b4974b4f321451ad5251ded85abb22c2b8b262da527dda1d031ab30
# rasterio's wheel links against libexpat, which the slim base does not include.
RUN apt update && apt upgrade -y \
  && apt install libexpat1 -y \
  && rm -rf /var/lib/apt/lists/*

ENV CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

COPY runtimes/ /tmp/runtimes
RUN --mount=from=uv,source=/uv,target=/usr/local/bin/uv \
    UV_PROJECT_ENVIRONMENT=/usr/local uv sync --project /tmp/runtimes --locked --no-editable --no-cache --compile-bytecode --extra server
# The app runs without pip, so it stays out of the image.
RUN rm -rf /tmp/runtimes && python -m pip uninstall -y pip setuptools wheel

RUN groupadd -g 1000 user && \
    useradd -u 1000 -g user -s /bin/bash -m user

USER user

ENV HOST 0.0.0.0
ENV PORT 80

CMD uvicorn titiler_md_demo.main:app --host ${HOST} --port ${PORT}
