from django import forms
from django.contrib.auth.models import User
from .models import Event, Category, Booking, Review, Subscription, Ticket


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'category', 'status', 'organizer_name', 'organizer_email', 'image', 'featured']

# Custom BookingForm for booking flow
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['ticket', 'quantity']
        widgets = {
            'ticket': forms.Select(attrs={
                'class': 'form-select',
                'id': 'ticket-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'id': 'quantity-input'
            })
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.event:
            available_tickets = self.event.tickets.filter(available_qty__gt=0)
            self.fields['ticket'].queryset = available_tickets
            self.fields['ticket'].empty_label = "Select ticket type"
            self.fields['quantity'].initial = 1

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        ticket = self.cleaned_data.get('ticket')
        if ticket and quantity > ticket.available_qty:
            raise forms.ValidationError(
                f"Only {ticket.available_qty} tickets available for {ticket.ticket_type}."
            )
        return quantity

# AdminBookingForm for admin dashboard
class AdminBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'ticket', 'quantity', 'status']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['booking', 'rating', 'comment']

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['event', 'ticket_type', 'price', 'total_quantity', 'description']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_active']


class EventSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Search events, categories, or locations...'
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Event.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    sort_by = forms.ChoiceField(
        choices=[
            ('date', 'Date'),
            ('price', 'Price'),
            ('popular', 'Popularity'),
            ('rating', 'Rating'),
            ('alphabetical', 'Name'),
        ],
        required=False,
        initial='date',
        widget=forms.Select(attrs={'class': 'form-select'})
    )