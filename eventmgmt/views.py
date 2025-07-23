from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, request
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .models import Event, Ticket, Booking, Review, Subscription, Category
from .forms import BookingForm, EventSearchForm, ReviewForm, CategoryForm, EventForm, SubscriptionForm, TicketForm, UserForm, AdminBookingForm
import smtplib

from django.shortcuts import redirect
import smtplib
from django.shortcuts import redirect
from django.contrib import messages
from .models import Subscription  # Ensure this is your Subscription model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User


def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if not Subscription.objects.filter(email=email).exists():
                Subscription.objects.create(email=email)

                # Send email
                from_email = 'himabindueluri15@gmail.com'
                to = email
                subject = 'Your subscription'
                message = f"Subject: {subject}\n\nThank you for registering in EventFlow"

                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(from_email, 'uqfu lbev ymgq wvwl')  # App password
                    server.sendmail(from_email, to, message)
                    server.quit()
                    messages.success(request, "Thank you for subscribing! A confirmation email has been sent.")
                except Exception as e:
                    print(f"Error sending email: {e}")
                    messages.warning(request, "Subscribed successfully, but failed to send confirmation email.")
            else:
                messages.info(request, "You are already subscribed.")
        else:
            messages.error(request, "Please enter a valid email address.")

        return redirect(request.META.get('HTTP_REFERER', 'event_list'))

    return redirect('event_list')


def ajax_event_filter(request):
    category = request.GET.get('category')
    status = request.GET.get('status')

    events = Event.objects.all()
    if category:
        events = events.filter(category=category)
    if status:
        events = events.filter(status=status)

    html = render_to_string('eventmgmt/partials/event_list.html', {'events': events})
    return JsonResponse({'events_html': html})
def event_list(request):
    events = Event.objects.filter(status='Active')
    form = EventSearchForm(request.GET or None)

    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        sort_by = form.cleaned_data.get('sort_by')

        if search_query:
            events = events.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(organizer_name__icontains=search_query)
            )

        if category:
            events = events.filter(category=category)

        if status:
            events = events.filter(status=status)

        if sort_by == 'price':
            events = sorted(events, key=lambda e: e.min_price)
        elif sort_by == 'popular':
            events = sorted(events, key=lambda e: e.total_tickets_sold, reverse=True)
        elif sort_by == 'rating':
            events = sorted(events, key=lambda e: e.average_rating, reverse=True)
        elif sort_by == 'alphabetical':
            events = events.order_by('title')
        else:
            events = events.order_by('date', 'time')

    featured_events = Event.objects.filter(status='Active', featured=True)[:3]

    context = {
        'events': events,
        'featured_events': featured_events,
        'form': form,
    }
    return render(request, 'eventmgmt/event_list.html', context)

#def home(request):
 #   query = request.GET.get('q')
  #  if query:
   #     events = Event.objects.filter(title__icontains=query)
    #else:
      #  events = Event.objects.all()
   # return render(request, 'base.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    available_tickets = event.tickets.filter(available_qty__gt=0)

    user = request.user if request.user.is_authenticated else None

    booking_form = BookingForm(event=event, user=user)
    reviews = Review.objects.filter(booking__ticket__event=event).order_by('-review_date')[:5]

    # Hide booking form if ?viewonly=1 is in the query params
    show_booking = request.GET.get('viewonly') != '1'

    context = {
        'event': event,
        'booking_form': booking_form,
        'available_tickets': available_tickets,
        'reviews': reviews,
        'show_booking': show_booking,
    }
    return render(request, 'eventmgmt/event_detail.html', context)

@require_POST
def book_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.is_sold_out:
        messages.error(request, 'This event is sold out.')
        return redirect('event_detail', pk=pk)

    user = request.user if request.user.is_authenticated else None

    form = BookingForm(request.POST, event=event, user=user)
    if form.is_valid():
        booking = form.save(commit=False)
        booking.user = user
        booking.save()
        # Redirect to payment page instead of confirming immediately
        return redirect('payment_page', booking_id=booking.id)
    else:
        messages.error(request, 'Please correct the errors below.')
        available_tickets = event.tickets.filter(available_qty__gt=0)
        reviews = Review.objects.filter(booking__ticket__event=event).order_by('-review_date')[:5]

        context = {
            'event': event,
            'booking_form': form,
            'available_tickets': available_tickets,
            'reviews': reviews,
        }
        return render(request, 'eventmgmt/event_detail.html', context)

@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != 'Cancelled':
        booking.status = 'Cancelled'
        booking.save()
        messages.success(request, 'Your booking has been cancelled.')
    else:
        messages.info(request, 'This booking is already cancelled.')
    return redirect('my_bookings')

def my_bookings(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your bookings.")
        return redirect('login')

    user = request.user
    bookings = Booking.objects.filter(user=user).exclude(status='Cancelled').order_by('-booking_date')

    total_spent = sum(booking.total_price for booking in bookings if booking.status == 'Confirmed')
    confirmed_bookings = bookings.filter(status='Confirmed').count()

    context = {
        'bookings': bookings,
        'total_spent': total_spent,
        'confirmed_bookings': confirmed_bookings,
    }
    return render(request, 'eventmgmt/my_bookings.html', context)

def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if not request.user.is_authenticated or booking.user != request.user:
        messages.error(request, 'You can only review your own bookings.')
        return redirect('my_bookings')

    if hasattr(booking, 'review'):
        messages.info(request, 'You have already reviewed this event.')
        return redirect('my_bookings')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('my_bookings')
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'booking': booking,
    }
    return render(request, 'eventmgmt/add_review.html', context)

def get_ticket_info(request):
    ticket_id = request.GET.get('ticket_id')
    if ticket_id:
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            return JsonResponse({
                'price': float(ticket.price),
                'available_qty': ticket.available_qty,
                'description': ticket.description,
            })
        except Ticket.DoesNotExist:
            pass

    return JsonResponse({'error': 'Ticket not found'}, status=404)


def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        # Simulate payment processing
        booking.status = 'Confirmed'
        booking.save()
        messages.success(request, 'Booked successfully!')
        return redirect('my_bookings')
    return render(request, 'eventmgmt/payment.html', {'booking': booking})

def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    ticket_text = (
        f"Event: {booking.ticket.event.title}\n"
        f"Date: {booking.ticket.event.date}\n"
        f"Time: {booking.ticket.event.time}\n"
        f"Location: {booking.ticket.event.location}\n"
        f"Ticket Type: {booking.ticket.ticket_type}\n"
        f"Quantity: {booking.quantity}\n"
        f"Booking Reference: {booking.booking_reference}\n"
        f"Name: {booking.user.get_full_name() or booking.user.username}\n"
    )
    response = HttpResponse(ticket_text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.booking_reference}.txt"'
    return response

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    context = {}
    # Handle form submissions
    if request.method == 'POST':
        if 'add_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
        else:
            category_form = CategoryForm()
        if 'add_event' in request.POST:
            event_form = EventForm(request.POST, request.FILES)
            if event_form.is_valid():
                event_form.save()
        else:
            event_form = EventForm()
        if 'add_booking' in request.POST:
            booking_form = AdminBookingForm(request.POST)
            if booking_form.is_valid():
                booking_form.save()
        else:
            booking_form = AdminBookingForm()
        if 'add_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_form.save()
        else:
            review_form = ReviewForm()
        if 'add_subscription' in request.POST:
            subscription_form = SubscriptionForm(request.POST)
            if subscription_form.is_valid():
                subscription_form.save()
        else:
            subscription_form = SubscriptionForm()
        if 'add_ticket' in request.POST:
            ticket_form = TicketForm(request.POST)
            if ticket_form.is_valid():
                ticket_form.save()
        else:
            ticket_form = TicketForm()
        if 'add_user' in request.POST:
            user_form = UserForm(request.POST)
            if user_form.is_valid():
                user_form.save()
        else:
            user_form = UserForm()
    else:
        category_form = CategoryForm()
        event_form = EventForm()
        booking_form = AdminBookingForm()
        review_form = ReviewForm()
        subscription_form = SubscriptionForm()
        ticket_form = TicketForm()
        user_form = UserForm()
    # Add forms and lists to context
    context['category_form'] = category_form
    context['event_form'] = event_form
    context['booking_form'] = booking_form
    context['review_form'] = review_form
    context['subscription_form'] = subscription_form
    context['ticket_form'] = ticket_form
    context['user_form'] = user_form
    context['categories'] = Category.objects.all()
    context['events'] = Event.objects.all()
    context['bookings'] = Booking.objects.all()
    context['reviews'] = Review.objects.all()
    context['subscriptions'] = Subscription.objects.all()
    context['tickets'] = Ticket.objects.all()
    context['users'] = User.objects.all()
    return render(request, 'eventmgmt/admin_dashboard.html', context)
