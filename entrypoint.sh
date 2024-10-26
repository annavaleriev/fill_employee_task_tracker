#!/bin/sh
#
## Прекращаем выполнение при ошибках
#set -e
#
## Проверка миграций и их применение
#echo "Применение миграций базы данных"
#python manage.py migrate
#
## Создание суперпользователя, если он не существует
#echo "Создание суперпользователя, если его нет"
#
#python manage.py shell << END
#from django.contrib.auth import get_user_model
#User = get_user_model()
#if not User.objects.filter(email='root@root.root').exists():
#    User.objects.create_superuser('$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
#    print('Суперпользователь создан')
#else:
#    print('Суперпользователь уже существует')
#END
#
## Запуск сервера
#python manage.py runserver 0.0.0.0:8000
#exec "$@"
#!/bin/sh

# Прекращаем выполнение при ошибках
set -e

# Проверка миграций и их применение
echo "Применение миграций базы данных"
python manage.py migrate

# Создание суперпользователя, если он не существует
echo "Создание суперпользователя, если его нет"

python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if email and password:
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(email=email, password=password)
        print('Суперпользователь создан')
    else:
        print('Суперпользователь уже существует')
else:
    print('Переменные окружения для суперпользователя не установлены')
END

# Запуск сервера
python manage.py runserver 0.0.0.0:8000
exec "$@"