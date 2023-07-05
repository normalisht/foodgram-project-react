import os
import subprocess
from time import sleep

from dotenv import load_dotenv

SUCCESS_LAUNCH = 'All processes up and running\r\n'
DOCKER_COMPOSE_COMMAND = ['sudo', 'docker', 'compose', '-f',
                          'docker-compose.production.yml']
DOCKER_WAIT_COMMAND = ['wait-for-docker', '&&']

subprocess.run(['pip', 'install', 'wait-for-docker'])
subprocess.run([*DOCKER_COMPOSE_COMMAND, 'down'])
subprocess.run([*DOCKER_COMPOSE_COMMAND, 'up', '-d'])

subprocess.run([*DOCKER_WAIT_COMMAND, *DOCKER_COMPOSE_COMMAND, 'exec',
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
