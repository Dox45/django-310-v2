# Impact Hub Lagos — Space Booking & Management System

A high-fidelity space booking and management system designed specifically around the booking requirements of a real coworking business. Built with **Django (Python)** and a premium **glassmorphic frontend** (inspired by the aesthetics of Stripe and the professional layout of Coursera), this system manages space listings, bookings, block periods, and customer profiles with real-time overlap validation.

---

## Features

### 🌟 Premium Glassmorphic Frontend
- **Showcase Grid**: Features rich cards displaying space details, capacities, prices, and booking limits.
- **Dynamic CSS & Gradients**: Styled using rich green and white gradients, glassmorphism card layouts (`backdrop-filter`), hover actions, and interactive loading micro-animations.
- **Real-Time AJAX Validation**: Leverages a background `/api/check-availability/` JSON endpoint. As soon as you pick a date/time, the system checks constraints and calculates the price dynamically without page reloads.
- **Visual Booking Receipt**: Submitting details pops up a clean receipt listing the booking reference, space name, dates, times, customer details, and price.

### ⚙️ Customized Business Admin Dashboard
- **Sorted Booking Matrix**: Standardized columns showing `Customer`, `Space`, `Date` (e.g. `Aug 19`), and `Time` (e.g. `10–12` or `09–17`).
- **Flexible Space Management**: Create spaces and modify space pricing directly inline.
- **Facility Blocking**: Register blocked dates/time ranges (e.g. for maintenance or private events). Blocked ranges instantly reflect on the frontend.
- **Admin Action - Booking Cancellation**: Cancel bookings in bulk with a custom action.
- **Customer CRM**: Maintain customer profiles, complete with inlined history of past bookings.

### 📅 Real-Time Booking Constraints
- **Hourly vs. Daily Bookings**:
  - **Hot Desk (Workspace)**: Booked per day (₦5,000/day). The date picker auto-locks the booking to a full work-day range (09:00 - 17:00).
  - **Room A (Meeting Room)**: Booked per hour (₦10,000/hour) for 1–4 hours. Requires selecting a start time and duration.
  - **Conference Room (Conference)**: Booked per hour (₦20,000/hour) for 1–4 hours.
- **Double Booking Prevention**: An overlapping time-slot query prevents two customers from booking the same room at the same time.
- **Hot Desk Allocator**: Booking a Hot Desk automatically allocates a free desk (e.g. Desk 1, Desk 2, or Desk 3) for that day. If all desks are occupied or blocked, it returns a friendly "fully booked" error.
- **Time Zone Alignment**: Configured for Nigerian local time (`Africa/Lagos`) to match Impact Hub Lagos business operations.

---

## Project Structure

```
django-sen-project/
│
├── booking/                     # Booking App
│   ├── static/                  # Static assets
│   │   └── booking/
│   │       ├── css/styles.css   # Green/white glassmorphic styles
│   │       └── js/app.js        # Form validation and AJAX calls
│   ├── templates/
│   │   └── booking/index.html   # Main booking landing page template
│   ├── management/commands/
│   │   └── seed_data.py         # Custom management command to seed spaces
│   ├── models.py                # Space, Customer, Booking, BlockedDate models
│   ├── admin.py                 # Customized Admin Site registration
│   ├── views.py                 # Page render and JSON API endpoints
│   ├── urls.py                  # App URL routing
│   └── tests.py                 # Automated unit tests
│
├── config/                      # Project Core Configuration
│   ├── settings.py              # Timezone, database, static files, installed apps
│   ├── urls.py                  # Project URL routing
│   └── wsgi.py / asgi.py
│
├── manage.py                    # Django management script
├── senvenv/                     # Python Virtual Environment
└── user_stories.md              # User stories & acceptance criteria document
```

---

## Installation & Setup

Follow these steps to run the application locally:

### 1. Prerequisite
Ensure Python 3.10+ is installed on your computer.

### 2. Enter Workspace and Activate Environment
Open your terminal in the `django-sen-project` directory. Run the following command to activate the virtual environment:
```bash
source senvenv/bin/activate
```

### 3. Install Django
Install Django inside the active environment:
```bash
pip install Django
```

### 4. Apply Database Migrations
Create and initialize the SQLite database:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Spaces (Required)
Seed the database with initial bookable desks, meeting rooms, and conference rooms:
```bash
python manage.py seed_data
```

### 6. Start the Server
Run the local Django development server:
```bash
python manage.py runserver
```
The application will be running at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## Administrative Credentials

You can log into the Django Admin dashboard at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) using these pre-configured credentials:
- **Username**: `admin`
- **Password**: `adminpassword`

From here, you can manage customer profiles, adjust space prices inline, block specific dates/times, and cancel bookings.

---

## Running Automated Tests

Run the unit test suite to verify the business logic, API validation, and booking constraints:
```bash
python manage.py test
```
The test suite validates:
1. Space initialization and parameters.
2. Automatic pricing calculation based on space rate and booking duration.
3. Correct enforcement of minimum/maximum duration limits.
4. Overlap detection (preventing room double bookings).
5. Respecting blocked calendar dates and hours.
6. Hot Desk automatic desk allocation (allocating Desk 1/2/3, detecting overflow).
7. Success/failure flows of the JSON APIs.
