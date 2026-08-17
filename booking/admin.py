from django.contrib import admin
from .models import Space, Customer, Booking, BlockedDate

@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_unit', 'price_unit', 'capacity', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price_per_unit', 'price_unit', 'is_active')
    ordering = ('category', 'name')


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('space', 'booking_date', 'start_time', 'end_time', 'duration', 'total_price', 'status')
    readonly_fields = ('total_price', 'created_at')
    ordering = ('-booking_date', '-start_time')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    inlines = [BookingInline]
    ordering = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'space_name', 'booking_date_display', 'booking_time_display', 'total_price', 'status')
    list_filter = ('status', 'booking_date', 'space__category', 'space')
    search_fields = ('customer__name', 'customer__email', 'space__name')
    actions = ['cancel_selected_bookings']
    
    # Customize header titles in booking columns to match specification exactly
    @admin.display(description='Customer')
    def customer_name(self, obj):
        return obj.customer.name

    @admin.display(description='Space')
    def space_name(self, obj):
        return obj.space.name

    @admin.display(description='Date')
    def booking_date_display(self, obj):
        return obj.booking_date.strftime("%b %d")

    @admin.display(description='Time')
    def booking_time_display(self, obj):
        # Format time range as 10-12 or 09-17
        start = obj.start_time.strftime("%H")
        end = obj.end_time.strftime("%H")
        return f"{start}–{end}"

    @admin.action(description='Cancel Selected Bookings')
    def cancel_selected_bookings(self, request, queryset):
        updated = queryset.update(status='Cancelled')
        self.message_user(request, f"{updated} booking(s) were successfully marked as Cancelled.")


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('space_display', 'date', 'time_range_display', 'reason')
    list_filter = ('date', 'space')
    search_fields = ('reason', 'space__name')
    ordering = ('-date',)

    @admin.display(description='Space Blocked')
    def space_display(self, obj):
        return obj.space.name if obj.space else "All Spaces"

    @admin.display(description='Blocked Hours')
    def time_range_display(self, obj):
        if obj.start_time and obj.end_time:
            return f"{obj.start_time.strftime('%H:%M')} – {obj.end_time.strftime('%H:%M')}"
        return "Full Day"

