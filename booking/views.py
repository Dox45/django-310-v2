from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from datetime import datetime, time, date, timedelta
import json

from .models import Space, Customer, Booking, BlockedDate

def index(request):
    # Retrieve spaces to show in the showcase
    spaces_info = []
    # We display categories for booking: Hot Desk, Meeting Room A, Conference Room
    # Let's query these categories
    categories = [
        {'id': 'hot_desk', 'name': 'Hot Desk', 'type': 'Workspace', 'price_display': '₦5,000/day', 'duration_display': '1 day'},
        {'id': 'meeting_room_a', 'name': 'Meeting Room A', 'type': 'Meeting room', 'price_display': '₦10,000/hour', 'duration_display': '1–4 hrs'},
        {'id': 'conference_room', 'name': 'Conference Room', 'type': 'Conference', 'price_display': '₦20,000/hour', 'duration_display': '1–4 hrs'},
    ]
    return render(request, 'booking/index.html', {'categories': categories})


def _get_target_space(space_type, booking_date, start_time, end_time):
    """
    Helper function to resolve the target Space model instance based on requested type.
    For hot_desk, it finds an available Workspace (Desk 1, Desk 2, Desk 3, etc.)
    For meeting_room_a, it returns 'Room A'
    For conference_room, it returns 'Conference Room'
    Returns (space_instance, error_message)
    """
    if space_type == 'meeting_room_a':
        try:
            space = Space.objects.get(name='Room A', category='Meeting room')
            return space, None
        except Space.DoesNotExist:
            return None, "Meeting Room A (Room A) is not configured in the system."
            
    elif space_type == 'conference_room':
        try:
            space = Space.objects.get(name='Conference Room', category='Conference')
            return space, None
        except Space.DoesNotExist:
            return None, "Conference Room is not configured in the system."
            
    elif space_type == 'hot_desk':
        # Retrieve all workspaces
        workspaces = Space.objects.filter(category='Workspace', is_active=True).order_by('name')
        if not workspaces.exists():
            return None, "No Workspace desks are configured in the system."
            
        # We need to find the first desk that is NOT booked or blocked on this date/time range
        # For workspaces, start_time is typically 09:00 and end_time is 17:00 (1 day)
        for desk in workspaces:
            # Check blocked dates
            blocked = BlockedDate.objects.filter(
                Q(space=desk) | Q(space__isnull=True),
                date=booking_date
            )
            is_blocked = False
            for block in blocked:
                if block.start_time is None or block.end_time is None:
                    is_blocked = True
                    break
                else:
                    if block.start_time < end_time and block.end_time > start_time:
                        is_blocked = True
                        break
            if is_blocked:
                continue
                
            # Check active bookings
            overlapping = Booking.objects.filter(
                space=desk,
                booking_date=booking_date,
                status='Confirmed',
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if not overlapping.exists():
                return desk, None # Found an available desk
                
        return None, "All hot desks are fully booked for the selected date."
        
    else:
        return None, "Invalid space selection."


def _validate_availability(space, booking_date, start_time, end_time):
    """
    Validates if a specific space is available (not blocked or booked).
    Returns (is_available, error_message)
    """
    # 1. Check if the space is blocked
    blocked = BlockedDate.objects.filter(
        Q(space=space) | Q(space__isnull=True),
        date=booking_date
    )
    for block in blocked:
        if block.start_time is None or block.end_time is None:
            return False, f"The space '{space.name}' is fully blocked on this date."
        else:
            if block.start_time < end_time and block.end_time > start_time:
                return False, f"The space '{space.name}' is blocked between {block.start_time.strftime('%H:%M')} and {block.end_time.strftime('%H:%M')}."

    # 2. Check for overlapping bookings
    overlapping = Booking.objects.filter(
        space=space,
        booking_date=booking_date,
        status='Confirmed',
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    if overlapping.exists():
        return False, f"The space '{space.name}' is already booked during this time range."

    return True, None


def check_availability_api(request):
    if request.method != 'GET':
        return JsonResponse({'available': False, 'message': 'Only GET requests allowed.'}, status=405)

    space_type = request.GET.get('space_type')
    date_str = request.GET.get('date')
    start_time_str = request.GET.get('start_time')
    duration_str = request.GET.get('duration')

    if not space_type or not date_str:
        return JsonResponse({'available': False, 'message': 'Missing space_type or date.'}, status=400)

    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'available': False, 'message': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    # Resolve date time bounds
    if space_type == 'hot_desk':
        # Hot desks are booked daily, default duration 1 day
        start_time = time(9, 0)
        end_time = time(17, 0)
        duration = 1
    else:
        # Meeting rooms require start_time and duration
        if not start_time_str or not duration_str:
            return JsonResponse({'available': False, 'message': 'Missing start_time or duration for hourly booking.'}, status=400)
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            duration = int(duration_str)
        except ValueError:
            return JsonResponse({'available': False, 'message': 'Invalid start_time (HH:MM) or duration.'}, status=400)

        # Calculate end time
        # Convert start time to datetime to add duration hours safely
        temp_dt = datetime.combine(date.today(), start_time) + timedelta(hours=duration)
        end_time = temp_dt.time()
        
        # Check that booking fits within single day
        if temp_dt.date() != date.today() or end_time == time(0, 0):
            # If it overflows to the next day
            if end_time == time(0, 0):
                # 24:00 (midnight) is acceptable as the end limit
                end_time = time(23, 59, 59)
            else:
                return JsonResponse({'available': False, 'message': 'Booking duration overflows into the next day.'}, status=400)

    # Find target space
    space, error_msg = _get_target_space(space_type, booking_date, start_time, end_time)
    if error_msg:
        return JsonResponse({'available': False, 'message': error_msg})

    # Validate availability (only needed for Room A & Conference room, as _get_target_space already validated Hot Desk)
    if space_type != 'hot_desk':
        available, error_msg = _validate_availability(space, booking_date, start_time, end_time)
        if not available:
            return JsonResponse({'available': False, 'message': error_msg})

    total_price = duration * space.price_per_unit
    
    return JsonResponse({
        'available': True,
        'space_name': space.name,
        'price': float(total_price),
        'duration_unit': space.price_unit,
        'message': f"Space is available. Total price: ₦{total_price:,.2f}"
    })


@csrf_exempt
@transaction.atomic
def create_booking_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST requests allowed.'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON body.'}, status=400)

    space_type = data.get('space_type')
    date_str = data.get('date')
    start_time_str = data.get('start_time')
    duration_str = data.get('duration')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone', '')

    if not space_type or not date_str or not name or not email:
        return JsonResponse({'success': False, 'message': 'Missing required fields (space_type, date, name, email).'}, status=400)

    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    # Determine times
    if space_type == 'hot_desk':
        start_time = time(9, 0)
        end_time = time(17, 0)
        duration = 1
    else:
        if not start_time_str or not duration_str:
            return JsonResponse({'success': False, 'message': 'Missing start_time or duration.'}, status=400)
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            duration = int(duration_str)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid start_time or duration.'}, status=400)

        temp_dt = datetime.combine(date.today(), start_time) + timedelta(hours=duration)
        end_time = temp_dt.time()
        if temp_dt.date() != date.today():
            if end_time == time(0, 0):
                end_time = time(23, 59, 59)
            else:
                return JsonResponse({'success': False, 'message': 'Booking duration overflows into the next day.'}, status=400)

    # Resolve space
    space, error_msg = _get_target_space(space_type, booking_date, start_time, end_time)
    if error_msg:
        return JsonResponse({'success': False, 'message': error_msg}, status=400)

    # Validate availability for non-hot desks (hot desks are already validated in _get_target_space)
    if space_type != 'hot_desk':
        available, error_msg = _validate_availability(space, booking_date, start_time, end_time)
        if not available:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)

    # Create or retrieve customer
    customer, created = Customer.objects.get_or_create(
        email=email.lower().strip(),
        defaults={'name': name.strip(), 'phone': phone.strip()}
    )
    if not created and name.strip():
        # Update name if changed
        customer.name = name.strip()
        if phone.strip():
            customer.phone = phone.strip()
        customer.save()

    # Create Booking
    try:
        booking = Booking(
            customer=customer,
            space=space,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            status='Confirmed'
        )
        booking.save()
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"Failed to create booking: {str(e)}"}, status=500)

    time_display = f"{booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}"
    if space_type == 'hot_desk':
        time_display = "Full Day (09:00 AM - 05:00 PM)"

    return JsonResponse({
        'success': True,
        'booking_id': booking.id,
        'message': 'Booking created successfully!',
        'details': {
            'customer_name': customer.name,
            'customer_email': customer.email,
            'space_name': space.name,
            'space_category': space.category,
            'date': booking.booking_date.strftime('%B %d, %Y'),
            'time_range': time_display,
            'duration': f"{booking.duration} {space.price_unit}(s)",
            'total_price': f"₦{booking.total_price:,.2f}"
        }
    })

