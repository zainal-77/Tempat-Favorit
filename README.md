# Tempat-Favorit CRUD
# Tempat Favorit

This is a simple Flask application with MySQL database, running in Docker containers.

## Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

Make sure you have the following software installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/tempat-favorit.git
    cd tempat-favorit
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. Set up MySQL configuration in `web/app.py`:

    ```python
    app.config['MYSQL_HOST'] = 'db'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'password'
    app.config['MYSQL_DB'] = 'tempat_favorit'
    ```

### Running the Application

1. Start the Docker containers:

    ```bash
    docker-compose up -d
    ```

2. Initialize the database:

    ```bash
    docker-compose exec web python app.py init-db
    ```

3. Access the application at [http://localhost:5000](http://localhost:5000).

### Stopping the Application

To stop the application and remove containers:

```bash
docker-compose down
