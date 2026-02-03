from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Proveedor, Llaves

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'profile']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
             return UserProfileSerializer(obj.profile).data
        return None

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class LlavesSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Llaves
        fields = '__all__'

    def get_proveedor_nombre(self, obj):
        return obj.proveedor.nombre if obj.proveedor else None
    
    def validate(self, data):
        """
        Validar que la combinación de código de llave y proveedor sea única
        """
        cod_llave = data.get('cod_llave')
        proveedor = data.get('proveedor')
        
        # Si estamos actualizando (self.instance existe), excluir el registro actual
        queryset = Llaves.objects.filter(cod_llave=cod_llave, proveedor=proveedor)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
            
        if queryset.exists():
            raise serializers.ValidationError(
                {"cod_llave": f"El código de llave '{cod_llave}' ya existe para este proveedor."}
            )
        return data

from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    preferred_provider_name = serializers.CharField(source='preferred_provider.nombre', read_only=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ['min_stock_alert', 'theme_color', 'active_provider_color', 'preferred_provider', 'preferred_provider_name']

from .models import HistorialSalida

class HistorialSalidaSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    llave_codigo = serializers.CharField(source='llave.cod_llave', read_only=True)

    class Meta:
        model = HistorialSalida
        fields = ['id', 'llave', 'llave_codigo', 'user', 'user_name', 'cantidad', 'fecha']

from .models import HistorialCompra

class HistorialCompraSerializer(serializers.ModelSerializer):
    llave_codigo = serializers.CharField(source='llave.cod_llave', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)

    class Meta:
        model = HistorialCompra
        fields = ['id', 'llave', 'llave_codigo', 'proveedor', 'proveedor_nombre', 'cantidad', 'precio_pago', 'fecha']
