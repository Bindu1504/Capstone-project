

# Register your models here.
from django.contrib import admin
from .models import Event, Ticket, Booking, Review, Category, Subscription


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'time', 'category', 'status', 'organizer_name', 'featured', 'total_capacity',
                    'total_tickets_sold']
    list_filter = ['category', 'status', 'featured', 'date']
    search_fields = ['title', 'description', 'location', 'organizer_name']
    list_editable = ['featured', 'status']
    ordering = ['date', 'time']
    date_hierarchy = 'date'

    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'category', 'organizer_name', 'featured')
        }),
        ('Date & Location', {
            'fields': ('date', 'time', 'location')
        }),
        ('Status & Media', {
            'fields': ('status', 'image')
        }),
    )

    def total_capacity(self, obj):
        return obj.total_capacity

    total_capacity.short_description = 'Total Capacity'

    def total_tickets_sold(self, obj):
        return obj.total_tickets_sold

    total_tickets_sold.short_description = 'Tickets Sold'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['event', 'ticket_type', 'price', 'total_quantity', 'available_qty', 'sold_quantity']
    list_filter = ['ticket_type', 'event__category', 'event__date']
    search_fields = ['event__title', 'ticket_type']
    ordering = ['event__date', 'price']

    def sold_quantity(self, obj):
        return obj.sold_quantity

    sold_quantity.short_description = 'Sold'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'user', 'ticket', 'quantity', 'total_price', 'booking_date', 'status']
    list_filter = ['status', 'booking_date', 'ticket__event__category']
    search_fields = ['user__username', 'user__email', 'ticket__event__title', 'booking_reference']
    readonly_fields = ['booking_reference', 'total_price', 'booking_date']
    ordering = ['-booking_date']
    date_hierarchy = 'booking_date'

    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'user', 'ticket', 'quantity', 'status')
        }),
        ('Payment Details', {
            'fields': ('total_price', 'booking_date')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'rating', 'star_display', 'review_date', 'get_event_title']
    list_filter = ['rating', 'review_date', 'booking__ticket__event__category']
    search_fields = ['booking__user__username', 'booking__ticket__event__title', 'comment']
    readonly_fields = ['review_date']
    ordering = ['-review_date']

    def get_event_title(self, obj):
        return obj.booking.ticket.event.title

    get_event_title.short_description = 'Event'

    def star_display(self, obj):
        return obj.star_display

    star_display.short_description = 'Rating'

admin.site.register(Subscription)