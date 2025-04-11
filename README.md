# title-proxy

> simple http proxy to fetch page titles, in use with my bookmaks project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Setup (with docker)

##### Prerequisites

- [Docker](https://www.docker.com/)
- [Python](https://www.python.org/) (for local development)

Clone the repo and navigate to the project directory:

```bash
git clone https://github.com/nocdn/title-proxy.git
cd title-proxy
```

Build the Docker image:

```bash
docker build -t title-proxy-service .
```

Run the Docker container:

```bash
docker run -d --restart=always --name title-proxy -p 8030:8000 title-proxy-service
```

(The `-d` flag runs the container in detached mode (so it runs in the background), and `-p 8030:8000` maps port 8000 in the container to port 8030 on your host machine. You can change the port mapping as needed to have this service accessible from other ports. The `--name` flag gives the container a name for easier management.)

The container will be available at `http://localhost:8030`, or at the ip address of the machine it's running on, eg: `http://<ip_address>:8030`.

### Usage

To use the proxy, you can use the following URL, eg:

`http://<ip_address>:8030/api/fetch-title?url=news.ycombinator.com`

Replace `<ip_address>` with the ip address of the machine running the proxy service, and `news.ycombinator.com` with the URL you want to fetch the title from.

The response should be a JSON object with a `title` property, eg:

```json
{
  "title": "Hacker News"
}
```

If the URL is not valid, the response will be a JSON object with an `detail` property, eg:

```json
{
  "detail": "URL parameter is required"
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
