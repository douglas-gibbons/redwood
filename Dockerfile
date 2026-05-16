FROM ubuntu:24.04

# Install uv for dependency management and make for running commands
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies required for Flet/Flutter Linux GUI
# Also install 'make' as the project uses it for running tasks
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libenchant-2-2 \
    libsecret-1-0 \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    libegl1 \
    libgl1 \
    libgl1-mesa-dri \
    libgles2 \
    at-spi2-core \
    make \
    ca-certificates \
    curl \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set up the workspace
RUN mkdir -p /app && chown ubuntu:ubuntu /app
WORKDIR /app

# Switch to the non-root ubuntu user
USER ubuntu

# Copy the project files with ubuntu ownership
COPY --chown=ubuntu:ubuntu . .

# Install dependencies using uv. We use --frozen to ensure it doesn't try to update lockfiles.
RUN uv sync --frozen

# Ensure the virtual environment binaries are in the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run a quick script to ensure Flet downloads its binaries during the docker build,
# so it doesn't do it at runtime. (Flet caches its flutter binary on first use)
RUN python -c "import flet.utils; flet.utils.get_current_script_dir()" || true


# To run this container, you will need to pass the X11 display socket and DISPLAY env var.
# Example:
# docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix redwood-gui
CMD ["gui"]
