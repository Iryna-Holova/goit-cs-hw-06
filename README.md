# Web Application with HTTP and Socket Servers

This project implements a simple web application with routing for two HTML pages: `index.html` and `message.html`. Static resources such as `style.css` and `logo.png` are processed during runtime. In case of a `404 Not Found error`, the application returns the `error.html` page. The HTTP server runs on port 3000.

A Socket server is created to handle form submission. The algorithm works as follows:

1. User enters data into the form.
2. The data is sent to the web application, which forwards it to the Socket server for processing using TCP protocol.
3. The Socket server parses the received byte-string into a dictionary and stores it in a MongoDB database.

The format of the MongoDB document is as follows:

```json
{
  "_id": {
    "$oid": "663fc874bd11d9f062874c04"
  },
  "username": "Iryna Holova",
  "message": "Hello World",
  "date": "2024-05-11 19:35:16"
}
```

The `date` key of each message represents the time the message was received, generated using `datetime.now()`.

## Requirements

- Python 3.10
- pymongo
- Docker
- Docker Compose

## Usage

1. Clone the repository.
2. Navigate to the project directory.
3. Run `docker-compose up --build` to build and start the containers.
4. Access the web application at `http://localhost`.

## File Structure

- `main.py`: Python script implementing the HTTP and Socket servers.
- `Dockerfile`: Instructions to build the Docker image.
- `docker-compose.yml`: Configuration for Docker Compose.
- `index.html`, `message.html`, `style.css`, `logo.png`, `error.html`: HTML, CSS, and image files for the web application.

## Docker Compose Configuration

- MongoDB is used as the database, with the official mongo Docker image.
- Health checks ensure the MongoDB service is healthy before starting the application.
