import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

def create_users():
    # Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created (password: admin123)")
    else:
        print("Superuser 'admin' already exists")

    # Normal User
    if not User.objects.filter(username='invitado').exists():
        user = User.objects.create_user('invitado', 'invitado@example.com', 'invitado123')
        user.first_name = "Usuario"
        user.last_name = "Invitado"
        user.save()
        print("Normal user 'invitado' created (password: invitado123)")
    else:
        print("Normal user 'invitado' already exists")

if __name__ == "__main__":
    create_users()
