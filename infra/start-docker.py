import subprocess
from time import sleep

SUCCESS_LAUNCH = 'All processes up and running\r\n'

subprocess.run('pip install docker-compose-wait'.split(' '))
subprocess.run('docker-compose stop'.split(' '))
subprocess.run('docker-compose up -d --build'.split(' '))

result = subprocess.run(['docker-compose-wait', '-f', 'docker-compose.yml'],
                        stdout=subprocess.PIPE)

while result.stdout.decode('UTF-8') != SUCCESS_LAUNCH:
    sleep(1)
    result = subprocess.run(
        ['docker-compose-wait', '-f', 'docker-compose.yml'],
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

subprocess.run(['docker-compose', 'exec', 'backend', 'python',
                'manage.py', 'shell', '-c',
                ("from users.models import User; "
                 "User.objects.create_superuser('admin', "
                 "'admin@example.com', 'admin')")],
               stdout=subprocess.DEVNULL,
               stderr=subprocess.STDOUT)
