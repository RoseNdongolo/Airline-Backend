from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, register_user, get_user,
    UserViewSet, AirportViewSet, AirlineViewSet, AircraftViewSet,
    FlightViewSet, BookingViewSet, PassengerViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'airports', AirportViewSet)
router.register(r'airlines', AirlineViewSet)
router.register(r'aircrafts', AircraftViewSet)
router.register(r'flights', FlightViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'passengers', PassengerViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management
    path('register/', register_user, name='register_user'),
    path('users/profile/', get_user, name='user_profile'),
    
    # Alias for token obtain
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
]