"""
Script para crear superusuarios en Django
Crea: Edgar Antayhua Saavedra y Manuel Antayhua Saavedra
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

# Datos de superusuarios a crear
superusers = [
    {
        'username': 'edgar',
        'first_name': 'Edgar',
        'last_name': 'Antayhua Saavedra',
        'email': 'edgar@example.com',
        'password': 'edgar123'
    },
    {
        'username': 'manuel',
        'first_name': 'Manuel',
        'last_name': 'Antayhua Saavedra',
        'email': 'manuel@example.com',
        'password': 'manuel123'
    }
]

# Crear superusuarios
for user_data in superusers:
    username = user_data['username']
    
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(
            username=username,
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        print(f'✓ Superusuario "{username}" creado exitosamente')
        print(f'  - Nombre: {user_data["first_name"]} {user_data["last_name"]}')
        print(f'  - Email: {user_data["email"]}')
        print(f'  - Contraseña: {user_data["password"]}')
    else:
        user = User.objects.get(username=username)
        # Actualizar datos si es necesario
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.email = user_data['email']
        user.save()
        print(f'⚠ Superusuario "{username}" ya existe (actualizado)')

print('\n✓ Proceso completado')
