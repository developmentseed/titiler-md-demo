FROM ghcr.io/astral-sh/uv:0.13.9@sha256:d3b601f0c7b118bc1753febf7c41cc80981df678445e0254284eecf84db79a7d AS uv

FROM python:3.12-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
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
