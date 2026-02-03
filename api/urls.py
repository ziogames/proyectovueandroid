from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProveedorViewSet, LlavesViewSet, UserViewSet, AIChatView, HistorialSalidaViewSet, HistorialCompraViewSet, ImageComparisonView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'llaves', LlavesViewSet)
router.register(r'historial', HistorialSalidaViewSet, basename='historial')
router.register(r'compras', HistorialCompraViewSet, basename='compras')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('ai/ask/', AIChatView.as_view(), name='ai_ask'),
    path('images/compare/', ImageComparisonView.as_view(), name='image_comparison'),
]
