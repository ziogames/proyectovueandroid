from django.db import models
from decimal import Decimal

class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()

    def __str__(self):
        return self.nombre

class Llaves(models.Model):
    TIPO_CHOICES = [
        ('house', 'Casa'),
        ('car', 'Auto'),
        ('menga', 'Menga Canal')
    ]

    cod_llave = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    img = models.ImageField(upload_to='llaves_img/', null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='llaves')
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.90'))
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='house', db_index=True)

    def __str__(self):
        return self.cod_llave

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cod_llave', 'proveedor'], name='unique_llave_per_proveedor')
        ]

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    min_stock_alert = models.IntegerField(default=300)
    theme_color = models.CharField(max_length=20, default='indigo')
    active_provider_color = models.CharField(max_length=20, default='indigo')
    preferred_provider = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class HistorialSalida(models.Model):
    llave = models.ForeignKey(Llaves, on_delete=models.CASCADE, related_name='historial')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.llave.cod_llave} - {self.cantidad} ({self.fecha})"

class HistorialCompra(models.Model):
    llave = models.ForeignKey(Llaves, on_delete=models.CASCADE, related_name='compras')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='compras_historial')
    cantidad = models.IntegerField()
    precio_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compra: {self.llave.cod_llave} - {self.cantidad} de {self.proveedor.nombre} ({self.fecha})"
