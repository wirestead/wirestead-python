# Exercise the published wheel ABI on actual Ubuntu userspaces. No C++ toolchain.
ARG UBUNTU_VERSION=24.04
FROM ghcr.io/astral-sh/uv:0.13.0 AS uv
FROM ubuntu:${UBUNTU_VERSION}
ARG UBUNTU_VERSION
COPY --from=uv /uv /usr/local/bin/uv
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates libstdc++6 python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
# Keep Focal's system Python intact; the other LTS versions use their default.
RUN if [ "$UBUNTU_VERSION" = "20.04" ]; then \
      uv python install 3.12 && \
      uv venv --python 3.12 --managed-python --seed /opt/consumer; \
    else \
      python3 -m venv /opt/consumer; \
    fi
ENV PATH="/opt/consumer/bin:${PATH}"
RUN python -c 'import sys; expected = {"20.04": (3, 12), "22.04": (3, 10), "24.04": (3, 12), "26.04": (3, 14)}[sys.argv[1]]; assert sys.version_info[:2] == expected, sys.version; print(sys.version)' "$UBUNTU_VERSION"
WORKDIR /tmp
CMD ["python", "/project/scripts/run_wheel_consumer_smoke.py", "--wheel-dir", "/project/wheel-artifacts", "--project-root", "/project"]
