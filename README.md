# Rest API service for yandex backend school

Rest API service written in Flask with commands listed in the assignment.pdf.

## Setup Instructions

### Docker way

First thing you are going to need is docker. [Install it.](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04)

Then buid the docker image usign your command prompt:

```bash
docker build -t rest_api
```

And run it:

```bash
docker run --rm -dp 8080:8080 rest_api
```

You can access the aplication using local_ip_adress:8080.

### Using your own hands

#### [Install python.](https://www.python.org/downloads/)

#### Install Required Python Modules

```bash
pip install -r requirements.txt
```

#### Start Web Server

To start the web server you need to run the following sequence of commands.

Set env variable of Flask app:

```bash
export FLASK_APP=main.py
```

Initialize db:

```bash
flask db init && flask db migrate && flask db upgrade
```

Run the Flask web server.

```bash
python main.py
```
