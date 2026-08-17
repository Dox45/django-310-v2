# Impact Hub Lagos — User Story & Acceptance Criteria Document

This document captures the user stories, customer personas, business requirements, and acceptance criteria for the Impact Hub Lagos Space Booking & Management System.

---

## User Personas

### 1. The Customer: John (Remote Consultant)
* **Goal**: Needs a professional meeting room in Lagos to host a client pitch for 2 hours.
* **Pain Points**: Needs instant confirmation of availability to assure his client, wants clear pricing upfront in Naira, and wants a clean, mobile-responsive checkout.
* **Role in System**: Uses the public landing page to find, check, and book "Meeting Room A".

### 2. The Customer: Amara (Freelance Software Developer)
* **Goal**: Needs a reliable desk workspace (Hot Desk) with continuous electricity and high-speed internet.
* **Pain Points**: Desks are often fully occupied. Wants to book a day desk in advance and get automatically allocated a space without manual staff intervention.
* **Role in System**: Uses the landing page to book a "Hot Desk" for 1 day.

### 3. The Admin/Owner: Tunde (Hub Manager / Business Owner)
* **Goal**: Maximize space utilization while maintaining pricing control and avoiding double-bookings.
* **Pain Points**: Managing physical desk numbers manually is prone to errors. Sometimes spaces are closed for private corporate events, and bookings need to be blocked out easily.
* **Role in System**: Logs into the Django Admin dashboard to manage spaces, adjust prices, block dates, view bookings, cancel bookings, and search customer records.

---

## User Stories & Acceptance Criteria

### Component 1: Customer Space Exploration & Booking

#### Story 1: Explore Available Spaces
* **As a** Customer visiting the landing page
* **I want to** view a structured showcase of available spaces, prices, and booking limits
* **So that** I can determine which space matches my professional requirements.
* **Acceptance Criteria**:
  * **Scenario 1: Viewing Space Details**
    * **Given** I am on the landing page,
    * **When** I look at the spaces section,
    * **Then** I must see:
      * **Hot Desk** (Workspace, ₦5,000/day, 1-day limit)
      * **Meeting Room A** (Meeting room, ₦10,000/hour, 1–4 hrs limit)
      * **Conference Room** (Conference space, ₦20,000/hour, 1–4 hrs limit)
  * **Scenario 2: Selection Action**
    * **Given** the space list is displayed,
    * **When** I click on a space card (e.g., "Meeting Room A"),
    * **Then** the card must highlight visually (green border/shadow), and the booking form must automatically lock into that space and enable the date selector.

#### Story 2: Real-Time Availability & Pricing Check
* **As a** Customer selecting a space
* **I want to** select my booking date, time, and duration and get a live pricing calculation and availability check
* **So that** I know if the slot is free and exactly how much it will cost before inputting personal details.
* **Acceptance Criteria**:
  * **Scenario 1: Room Booking Input Validation**
    * **Given** I have selected an hourly space (e.g. Meeting Room A),
    * **When** I select a date, start time, and duration (e.g., 2 hours),
    * **Then** the system must invoke the availability API in the background and compute the total price (₦20,000.00).
  * **Scenario 2: Hot Desk Time Auto-lock**
    * **Given** I have selected "Hot Desk",
    * **When** I select a date,
    * **Then** the start time and duration must be locked to "Full Day (09:00 - 17:00)" automatically, and the estimated total must update to ₦5,000.00.
  * **Scenario 3: Conflicting Slot Feedback**
    * **Given** another client has already booked Room A on August 19 from 10:00 AM to 12:00 PM,
    * **When** I check Room A on August 19 at 10:00 AM for 2 hours,
    * **Then** the system must show a prominent red error banner: *"The space 'Room A' is already booked during this time range."* and keep the submit button disabled.

#### Story 3: Complete Reservation & Confirm Receipt
* **As a** Customer with an available slot
* **I want to** enter my contact details and submit the form
* **So that** my booking is registered in the database, and I receive a receipt.
* **Acceptance Criteria**:
  * **Scenario 1: Seamless Checkout & Modal Popup**
    * **Given** my selected slot is available and I have entered my name ("John Doe") and email ("john@example.com"),
    * **When** I click "Confirm Booking",
    * **Then** the booking must be written to the database under the name and email, and a success receipt modal must pop up immediately.
  * **Scenario 2: Receipt Verification**
    * **Given** the booking has been confirmed,
    * **When** the success receipt modal opens,
    * **Then** it must display:
      * Unique Booking Reference (e.g., `#IHL-[booking_id]`)
      * Space Name (e.g., `Room A`)
      * Selected Date & Time (e.g., `August 19, 2026 - 10:00 AM - 12:00 PM`)
      * Customer details & total amount paid (e.g., `₦20,000.00`).

---

### Component 2: Business Admin & Space Management

#### Story 4: View Bookings Matrix
* **As an** Admin (Hub Manager)
* **I want to** log in to the admin panel and see a clean, sorted matrix of all bookings
* **So that** I can view daily schedules at a glance.
* **Acceptance Criteria**:
  * **Given** I am logged into the Django Admin dashboard,
  * **When** I navigate to the "Bookings" list view,
  * **Then** the table must display these columns explicitly:
    * **Customer** (showing Customer Name)
    * **Space** (showing physical room/desk name like Room A, Desk 3)
    * **Date** (formatted as Month Day, e.g. "Aug 19")
    * **Time** (formatted as 24-hour hour bounds, e.g. "10–12" or "09–17")
    * **Total Price** and **Status** (Confirmed / Cancelled)

#### Story 5: Block Unavailable Dates / Hours
* **As an** Admin (Hub Manager)
* **I want to** add a block for specific spaces or the entire hub for particular dates or hours
* **So that** customers cannot book spaces during private events or maintenance windows.
* **Acceptance Criteria**:
  * **Scenario 1: Full-Day Block**
    * **Given** I create a Blocked Date record for `Room A` on `2026-08-20` with start and end times empty,
    * **When** a customer attempts to check availability for Room A on August 20, 2026,
    * **Then** the frontend must show the slot is blocked and prevent booking.
  * **Scenario 2: Multi-Space (Hub-Wide) Block**
    * **Given** I create a Blocked Date record with space set to empty (null) on `2026-08-21`,
    * **When** a customer checks availability for *any* space on August 21, 2026,
    * **Then** the system must mark it as unavailable.

#### Story 6: Manage Space Prices & Active Statuses
* **As an** Admin (Hub Manager)
* **I want to** quickly change space prices and toggle availability
* **So that** I can adapt pricing dynamically without modifying code.
* **Acceptance Criteria**:
  * **Given** I am in the Spaces admin list,
  * **When** I change the price or toggle the active status directly in the table grid and click Save,
  * **Then** the changes must apply immediately, updating calculations for all future bookings.

#### Story 7: Manage Customers & Cancel Bookings
* **As an** Admin (Hub Manager)
* **I want to** cancel bookings and manage customer profiles
* **So that** I can handle refunds, cancellations, and client queries.
* **Acceptance Criteria**:
  * **Scenario 1: Bulk Booking Cancellation**
    * **Given** I am in the Bookings list,
    * **When** I check multiple bookings and select the "Cancel Selected Bookings" action,
    * **Then** their status must update to "Cancelled" and the customer's slot is instantly released.
  * **Scenario 2: Customer Profile Inline View**
    * **Given** I open a specific Customer's detail page,
    * **When** I look at the bottom of the form,
    * **Then** I must see an inline table of their complete booking history.

---

## Edge Case Handling Matrix

| Edge Case | System Behavior | Validation Layer |
| :--- | :--- | :--- |
| **Double Room Bookings** | Prevents overlapping times. Room A booked 10-12 cannot be booked at 11-13. | Database Query (Overlap check: `start_time < requested_end_time` AND `end_time > requested_start_time`). |
| **Hot Desk Overflow** | Allocates next free desk (Desk 1 -> Desk 2 -> Desk 3). If all 3 are booked, returns "fully booked". | View loops through workspaces, checking each desk's bookings. |
| **Blocked Dates** | Blocked dates (full-day or partial hours) override space availability. | Pre-check on `BlockedDate` model. |
| **Invalid Time Range** | End time <= Start time (e.g. 12:00 to 10:00). | Model `.clean()` method & frontend validator. |
| **Duration Over Limits** | Duration is less than `min_duration` or greater than `max_duration` (e.g., booking a room for 5 hours). | Model `.clean()` method & frontend selector limits. |
| **Lagos Time Zone** | Bookings are calculated in Local Nigerian Time (`Africa/Lagos`). | Django `settings.py` `TIME_ZONE = 'Africa/Lagos'`. |
| **Duplicate Customer Email**| If email exists, associate new booking with existing customer profile (and update name if changed). | Django `Customer.objects.get_or_create`. |
