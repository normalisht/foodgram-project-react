import subprocess
from time import sleep

import docker


def check_docker_compose():
    client = docker.from_env()
    containers = client.containers.list()

    for container in containers:
        labels = container.labels
        if 'com.docker.compose.project' in labels:
            return True

    return False


subprocess.run('docker-compose stop'.split(' '))
subprocess.run('docker-compose up -d --build'.split(' '))

while not check_docker_compose():
    sleep(1)

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'migrate'])

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'load_data'])

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'collectstatic', '--noinput'])

subprocess.run(['docker-compose', 'exec', 'backend', 'cp',
                '-r', '/app/collected_static/.', '/backend_static/static/'])

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'shell', '-c',
                ("from users.models import User; "
                 "User.objects.create_superuser('admin', "
                 "'admin@example.com', 'admin')")],
               stdout=subprocess.DEVNULL,
               stderr=subprocess.STDOUT)
