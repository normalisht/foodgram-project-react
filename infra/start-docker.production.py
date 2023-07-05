import os
import subprocess
from time import sleep

import docker
from dotenv import load_dotenv


def check_docker_compose():
    client = docker.from_env()
    containers = client.containers.list()

    for container in containers:
        labels = container.labels
        if 'com.docker.compose.project' in labels:
            return True

    return False


SUCCESS_LAUNCH = 'All processes up and running\r\n'
DOCKER_COMPOSE_COMMAND = ['sudo', 'docker', 'compose', '-f',
                          'docker-compose.production.yml']

subprocess.run([*DOCKER_COMPOSE_COMMAND, 'down'])
subprocess.run([*DOCKER_COMPOSE_COMMAND, 'up', '-d'])

while not check_docker_compose():
    sleep(1)

subprocess.run([*DOCKER_COMPOSE_COMMAND, 'exec',
                'backend', 'python', 'manage.py', 'migrate'])

subprocess.run([*DOCKER_COMPOSE_COMMAND, 'exec', 'backend', 'python',
                'manage.py', 'load_data'])

subprocess.run([*DOCKER_COMPOSE_COMMAND, 'exec', 'backend', 'python',
                'manage.py', 'collectstatic', '--noinput'])

subprocess.run([*DOCKER_COMPOSE_COMMAND, 'exec', 'backend', 'cp',
                '-r', '/app/collected_static/.', '/backend_static/static/'])

load_dotenv()

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

subprocess.run([*DOCKER_COMPOSE_COMMAND, 'exec', 'backend', 'python',
                'manage.py', 'shell', '-c',
                ("from users.models import User; "
                 f"User.objects.create_superuser('{ADMIN_USERNAME}', "
                 f"'{ADMIN_EMAIL}', '{ADMIN_PASSWORD}')")],
               stdout=subprocess.DEVNULL,
               stderr=subprocess.STDOUT)
