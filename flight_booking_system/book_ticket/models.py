from django.db import models
import uuid
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Admin'),
        (2, 'Airline Staff'),
        (3, 'Customer'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3)
    phone_number = models.CharField(max_length=20, blank=True)
    
    def is_admin(self):
        return self.user_type == 1
    
    def is_staff_member(self):
        return self.user_type == 2
    
    def is_customer(self):
        return self.user_type == 3

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Airline(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='airline_logos/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class Aircraft(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    registration_number = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.airline.name} - {self.model} ({self.registration_number})"




class Flight(models.Model):
    FLIGHT_TYPE_CHOICES = (
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first_class', 'First Class'),
    )

    flight_number = models.CharField(max_length=10, unique=True)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.SET_NULL, null=True, blank=True)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, null=True, blank=True)
    departure_airport = models.ForeignKey(Airport, related_name='departures', on_delete=models.CASCADE)
    arrival_airport = models.ForeignKey(Airport, related_name='arrivals', on_delete=models.CASCADE)

    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    
    flight_type = models.CharField(
        max_length=20,
        choices=FLIGHT_TYPE_CHOICES,
        default='economy'
    )

    def __str__(self):
        return f"{self.flight_number} – {self.departure_airport.code} to {self.arrival_airport.code}"



class Booking(models.Model):
    BOOKING_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE)
    booking_reference = models.CharField(max_length=10, unique=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    seats_booked = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_reference} for {self.user.username}"
    

class Passenger(models.Model):
    booking = models.ForeignKey(Booking, related_name='passengers', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Payment for {self.booking.booking_reference}"