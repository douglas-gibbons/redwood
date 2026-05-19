# Running Redwood in Docker

This guide explains how to build and run the Redwood application within an isolated Docker container. The container runs a local web server, allowing you to access the GUI directly from your web browser.

## 1. Build the Image

To get started, build the Docker container using the provided `Dockerfile`. This will install all system dependencies and the Redwood Python application.

```bash
docker build -t redwood .
```

## 2. Run the Container

Start the container and map the internal web server port (8550) to your host machine:

```bash
docker run -it --rm -p 8550:8550 redwood
```

If you want t include your local redwood configuration:

```bash
docker run -it --rm -v ~/.config/redwood:/home/ubuntu/.config/redwood -p 8550:8550 redwood
```



## 3. Access the GUI

Once the container is running, open your web browser and navigate to [localhost:8550](http://localhost:8550).


## Troubleshooting

### Port Already in Use
If you see an error indicating that port `8550` is already in use, you can map it to a different port on your host machine. For example, to use port `9000`:

```bash
docker run -it --rm -p 9000:8550 redwood
```
Then access it at [localhost:9000](http://localhost:9000)]
