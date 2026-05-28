docker run --rm ubuntu:24.04 bash -c "apt-get update && apt-get install -y libglib2.0-0 && dpkg -s libglib2.0-0 | grep Version"
