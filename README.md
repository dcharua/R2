# Flask R2

This project integrates R2 with Flask using:
- [Blueprints](http://flask.pocoo.org/docs/0.12/blueprints/) for scalability.
- [flask_login](https://flask-login.readthedocs.io/en/latest/) for the login system (passwords hashed with bcrypt).
- [flask_migrate](https://flask-migrate.readthedocs.io/en/latest/).

Flask-R2 also comes with a robust CI/CD pipeline using:
- The [Pytest](https://docs.pytest.org/en/latest/) framework for the test suite (see the `tests` folder).
- A [PostgreSQL](https://www.postgresql.org/) database (optional; see below for installation instructions).
- [Travis CI](https://travis-ci.org/afourmy/flask-R2) (automated testing)
- [Coverage](https://coveralls.io/github/afourmy/flask-R2) to measure the code coverage of the tests.
- [Selenium](https://www.seleniumhq.org/) to test the application with headless chromium.
- A `Dockerfile` showing how to containerize the application with gunicorn, and a [Docker image](https://hub.docker.com/r/afourmy/flask-R2/) available on dockerhub, and integrated to the CI/CD pipeline (see instructions below).
- A `docker-compose` file to start Flask-R2 with `nginx`, `gunicorn` and a PostgreSQL database.

Here is an example of a real project implemented using Flask-R2:
- [Online demo](http://afourmy.pythonanywhere.com/)
- [Source code](https://github.com/afourmy/eNMS)

This project shows:
- how back-end and front-end can interact responsively with AJAX requests.
- how to implement a graph model with SQLAlchemy and use D3.js for [graph visualization](http://afourmy.pythonanywhere.com/views/logical_view).
- how to implement a [workflow automation](http://afourmy.pythonanywhere.com/workflows/manage_BGP-configuration-workflow) system using Vis.js.
- how to use [Leaflet.js](http://afourmy.pythonanywhere.com/views/geographical_view) for GIS programming.
- how to use [Flask APScheduler](https://github.com/viniciuschiele/flask-apscheduler) to implement crontab-like features.

## Run Flask R2 with a SQLite database

### (Optional) Set up a [virtual environment](https://docs.python.org/3/library/venv.html)

### 1. Get the code
    git clone https://github.com/afourmy/flask-R2.git
    cd flask-R2

### 2. Install requirements
    pip install -r requirements.txt
    
    2.1 Makse Sure you have ODBC Driver 17 for SQL Server 
    https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-2017

### 3. Set the FLASK_APP environment variable
    (Windows) set FLASK_APP=R2.py
              set  FLASK_ENV=development

    (Unix) export FLASK_APP=R2.py
	   export FLASK_ENV=development
### 4. Run the application
    flask run

### 4. Go to http://server_address:5000/, create an account and log in

### 2. Export the following environment variables
    export APP_CONFIG_MODE=Production
    export APP_DATABASE_PASSWORD=your-password

### 3. Follow the steps described in the previous section

## Run Flask R2 in a docker container

### 1. Fetch the image on dockerhub
    docker run -d -p 5000:5000 --name R2 --restart always afourmy/R2

### 2. Go to http://server_address:5000/, create an account and log in

## Run Flask R2 in a docker container with nginx and a PostgreSQL database

### 2. Start all services
    sudo docker-compose pull && sudo docker-compose build && sudo docker-compose up -d

### 3. Go to http://server_address, create an account and log in


### SQLACHEMY TUTORIALS https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database


### CRUD 
https://www.codementor.io/garethdwyer/building-a-crud-application-with-flask-and-sqlalchemy-dm3wv7yu2

### SQL Relationships
https://www.pythoncentral.io/migrate-sqlalchemy-databases-alembic/