# Running Redwood in Docker

This guide explains how to build and run the Redwood GUI application within an isolated Docker container on Linux or macOS.

## 1. Build the Image

To get started, build the Docker container using the provided `Dockerfile`. This will install all system dependencies, including `uv`, `npx`, and required GTK/OpenGL graphics libraries.

```bash
docker build -t redwood-gui .
```

## 2. Prepare the Host Environment & Run

Since Redwood is a graphical application, the Docker container needs a way to draw windows on your host machine's screen. The setup depends on your operating system.

### Linux

Linux natively uses X11 or Wayland, making it straightforward to pass the display socket and GPU device.

1. **Authorize local connections**: 
   ```bash
   xhost +local:
   ```
   *(Note: If `xhost` is missing, install it via `sudo apt install x11-xserver-utils` or equivalent).*

2. **Run the Container**:
   Launch the container, passing the display and GPU device for hardware-accelerated OpenGL rendering (required by the Flet engine).
   ```bash
   docker run -it --rm \
     -e DISPLAY=$DISPLAY \
     -v /tmp/.X11-unix:/tmp/.X11-unix \
     --device /dev/dri \
     redwood-gui
   ```

### macOS

macOS requires an external X11 server like **XQuartz** to render Linux GUI apps from a Docker container. Hardware acceleration (`/dev/dri`) is not available, so it falls back to software rendering (llvmpipe).

1. **Install and Configure XQuartz**:
   ```bash
   brew install --cask xquartz
   ```
   - Open **XQuartz** from your Applications folder.
   - Go to **XQuartz -> Settings** (or Preferences) -> **Security** tab.
   - Check the box for **"Allow connections from network clients"**.
   - **Restart XQuartz** (or log out of your Mac and log back in) for the setting to take effect.

2. **Authorize local connections**:
   Open a terminal and authorize connections from your local machine:
   ```bash
   xhost +localhost
   ```

3. **Run the Container**:
   Pass the `host.docker.internal` network address so the container can reach your Mac's XQuartz server.
   ```bash
   docker run -it --rm \
     -e DISPLAY=host.docker.internal:0 \
     redwood-gui
   ```


## Troubleshooting

### `cannot open display` or `Gtk-WARNING`
If you encounter `cannot open display: :1` or similar GTK warnings, double-check that you ran `xhost +local:` on your host machine prior to starting the container.

### Wayland Desktop Environments
If you use Wayland (default on newer Ubuntu/Fedora) and the standard XWayland approach above fails, you may need to explicitly mount your Wayland socket as well:
```bash
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -e WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /run/user/$(id -u)/wayland-0:/run/user/$(id -u)/wayland-0 \
  --device /dev/dri \
  redwood-gui
```

### Missing OpenGL / ATK Errors
The `Dockerfile` is pre-configured with Mesa graphics drivers, `libgles2`, and `at-spi2-core`. If you continue to see `No GL implementation is available` in the terminal output, ensure your host GPU drivers are correctly installed and that the `/dev/dri` directory exists on your host machine.
