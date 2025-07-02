from rest_framework import serializers
from .models import Booking, Flight, Passenger, User, Aircraft, Airline, Airport, Payment
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

# ✅ User Registration Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'user_type', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # ✅ Ensure password is hashed
        user = User.objects.create_user(**validated_data)
        return user

# ✅ User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['date_joined', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        required_fields = ['first_name', 'last_name', 'phone_number']
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            raise serializers.ValidationError(
                f"Profile incomplete. Missing fields: {', '.join(missing)}"
            )
        return data

    def update(self, instance, validated_data):
        profile_fields = ['first_name', 'last_name', 'phone_number']
        for field in profile_fields:
            if field in validated_data and not getattr(instance, field):
                setattr(instance, field, validated_data[field])
        return super().update(instance, validated_data)

# ✅ Custom Login Serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return data

# ✅ Custom Login View
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from rest_framework import serializers
from .models import Booking, Passenger, Flight

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        exclude = ['booking']  # or explicitly list fields if you prefer

class BookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, write_only=True)
    flight_id = serializers.IntegerField(write_only=True)
    flight = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'flight_id', 'flight', 'user', 'seats_booked',
            'total_price', 'status', 'booking_reference', 'passengers'
        ]
        read_only_fields = ['id', 'user', 'total_price', 'status', 'booking_reference', 'flight']

    def get_flight(self, obj):
        return {
            "flight_number": obj.flight.flight_number,
            "flight_type": obj.flight.flight_type
        }

    def validate(self, data):
        flight = Flight.objects.get(id=data['flight_id'])
        if data['seats_booked'] > flight.available_seats:
            raise serializers.ValidationError(
                f"Only {flight.available_seats} seats available."
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        validated_data.pop('user', None)

        flight_id = validated_data.pop('flight_id')
        passengers_data = validated_data.pop('passengers', [])

        flight = Flight.objects.get(id=flight_id)
        seats = validated_data['seats_booked']
        total_price = seats * flight.base_price

        booking = Booking.objects.create(
            user=user,
            flight=flight,
            total_price=total_price,
            **validated_data
        )

        for p in passengers_data:
            Passenger.objects.create(booking=booking, **p)

        return booking


# ✅ Airport Serializer
class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['id', 'code', 'name', 'city', 'country']

# ✅ Airline Serializer
class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ['id', 'name', 'logo']

# ✅ Aircraft Serializer
class AircraftSerializer(serializers.ModelSerializer):
    airline = serializers.PrimaryKeyRelatedField(queryset=Airline.objects.all())

    class Meta:
        model = Aircraft
        fields = ['id', 'airline', 'model', 'capacity', 'registration_number']

# ✅ Flight Serializer
class FlightSerializer(serializers.ModelSerializer):
    airline = AirlineSerializer(read_only=True)
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    airline_id = serializers.PrimaryKeyRelatedField(queryset=Airline.objects.all(), source='airline', write_only=True)
    departure_airport_id = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all(), source='departure_airport', write_only=True)
    arrival_airport_id = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all(), source='arrival_airport', write_only=True)

    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'airline', 'airline_id',
            'departure_airport', 'departure_airport_id',
            'arrival_airport', 'arrival_airport_id',
            'departure_time', 'arrival_time',
            'base_price', 'available_seats', 'flight_type'
        ]


    class Meta:
        model = Flight
        fields = ['id', 'airline', 'airline_id', 'aircraft', 'flight_number', 'departure_airport', 'departure_airport_id', 'arrival_airport', 'arrival_airport_id', 'departure_time', 'arrival_time', 'base_price', 'available_seats']

# ✅ Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
