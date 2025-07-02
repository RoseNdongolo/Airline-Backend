from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Aircraft)
admin.site.register(Flight)
admin.site.register(Booking)
admin.site.register(Passenger)
admin.site.register(Payment)
