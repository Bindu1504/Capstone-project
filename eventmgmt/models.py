from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name




class Event(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
        ('Draft', 'Draft'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    organizer_name = models.CharField(max_length=100)
    organizer_email = models.EmailField(blank=True, null=True)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})

    @property
    def total_tickets_sold(self):
        return sum(booking.quantity for booking in Booking.objects.filter(
            ticket__event=self, status='Confirmed'
        ))

    @property
    def total_capacity(self):
        return sum(ticket.total_quantity for ticket in self.tickets.all())

    @property
    def available_spots(self):
        return self.total_capacity - self.total_tickets_sold

    @property
    def is_sold_out(self):
        return self.available_spots <= 0

    @property
    def is_almost_full(self):
        if self.total_capacity > 0:
            return self.available_spots <= (self.total_capacity * 0.1)
        return False

    @property
    def min_price(self):
        tickets = self.tickets.all()
        if tickets:
            return min(ticket.price for ticket in tickets)
        return 0

    @property
    def average_rating(self):
        reviews = Review.objects.filter(booking__ticket__event=self)
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    @property
    def review_count(self):
        return Review.objects.filter(booking__ticket__event=self).count()


class Ticket(models.Model):
    TICKET_TYPE_CHOICES = [
        ('General', 'General Admission'),
        ('VIP', 'VIP'),
        ('Premium', 'Premium'),
        ('Student', 'Student'),
        ('Early Bird', 'Early Bird'),
        ('Group', 'Group'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    ticket_type = models.CharField(max_length=50, choices=TICKET_TYPE_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    total_quantity = models.IntegerField()
    available_qty = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.event.title} - {self.ticket_type}"

    @property
    def sold_quantity(self):
        return self.total_quantity - self.available_qty

    @property
    def is_available(self):
        return self.available_qty > 0

    def save(self, *args, **kwargs):
        if not self.pk:  # New ticket
            self.available_qty = self.total_quantity
        super().save(*args, **kwargs)


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='bookings')
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    booking_reference = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"{self.user.username} - {self.ticket.event.title}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import random
            import string
            self.booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Service fee is 5% of the total ticket price
        ticket_total = self.ticket.price * self.quantity
        service_fee = Decimal('0.05') * ticket_total
        self.total_price = ticket_total + service_fee

        super().save(*args, **kwargs)

        # Update ticket availability
        if self.status == 'Confirmed':
            self.ticket.available_qty = max(0, self.ticket.available_qty - self.quantity)
            self.ticket.save()

    @property
    def service_fee(self):
        ticket_total = self.ticket.price * self.quantity
        return Decimal('0.05') * ticket_total


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    review_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-review_date']

    def __str__(self):
        return f"{self.booking.user.username} - {self.booking.ticket.event.title} ({self.rating} stars)"

    @property
    def star_display(self):
        return '★' * self.rating + '☆' * (5 - self.rating)


class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email