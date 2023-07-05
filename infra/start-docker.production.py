import subprocess
from time import sleep
import os
from dotenv import load_dotenv

SUCCESS_LAUNCH = 'All processes up and running\r\n'
DOCKER_COMPOSE_COMMAND = ['sudo', 'docker', 'compose', '-f',
                          'docker-compose.production.yml']

subprocess.run(['pip', 'install', 'docker-compose-wait'])
subprocess.run([*DOCKER_COMPOSE_COMMAND, 'down'])
subprocess.run([DOCKER_COMPOSE_COMMAND, 'up', '-d'])

result = subprocess.run(
    ['docker-compose-wait', '-f', 'docker-compose.production.yml'],
    stdout=subprocess.PIPE
)

while result.stdout.decode('UTF-8') != SUCCESS_LAUNCH:
    sleep(1)
    result = subprocess.run(
        ['docker-compose-wait', '-f', 'docker-compose.production.yml'],
        stdout=subprocess.PIPE
    )

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'migrate'])

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'load_data'])

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'collectstatic', '--noinput'])

subprocess.run(['docker-compose', 'exec', 'backend', 'cp',
                '-r', '/app/collected_static/.', '/backend_static/static/'])

load_dotenv()

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'shell', '-c',
                ("from users.models import User; "
                 f"User.objects.create_superuser('{ADMIN_USERNAME}', "
                 f"'{ADMIN_EMAIL}', '{ADMIN_PASSWORD}')")],
               stdout=subprocess.DEVNULL,
               stderr=subprocess.STDOUT)
