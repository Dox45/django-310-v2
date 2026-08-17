// Impact Hub Lagos Space Booking - Frontend Client Logic

// State variables
let currentSpace = null;
let spaceRates = {
    'hot_desk': { name: 'Hot Desk', rate: 5000, type: 'Workspace', unit: 'day' },
    'meeting_room_a': { name: 'Meeting Room A (Room A)', rate: 10000, type: 'Meeting room', unit: 'hour' },
    'conference_room': { name: 'Conference Room', rate: 20000, type: 'Conference', unit: 'hour' }
};

// DOM Elements
const spaceTypeInput = document.getElementById('space_type');
const spaceDisplayBox = document.getElementById('space-display-box');
const dateInput = document.getElementById('booking_date');
const timeGroup = document.getElementById('time-group');
const startTimeSelect = document.getElementById('start_time');
const durationGroup = document.getElementById('duration-group');
const durationSelect = document.getElementById('duration');
const hotdeskInfoGroup = document.getElementById('hotdesk-info-group');
const customerFields = document.querySelectorAll('.customer-info-fields');
const customerInputs = document.querySelectorAll('.customer-info-fields input');
const statusAlert = document.getElementById('status-alert');
const priceBox = document.getElementById('price-box');
const rateValue = document.getElementById('rate-value');
const durationValue = document.getElementById('duration-value');
const totalValue = document.getElementById('total-value');
const submitBtn = document.getElementById('submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const successModal = document.getElementById('success-modal');

// Set min date on date picker to today
const today = new Date().toISOString().split('T')[0];
dateInput.min = today;

// Event Listeners for availability check
dateInput.addEventListener('change', checkAvailability);
startTimeSelect.addEventListener('change', checkAvailability);
durationSelect.addEventListener('change', checkAvailability);

/**
 * Handle Space Selection Card click
 */
function selectSpace(spaceId) {
    currentSpace = spaceId;
    spaceTypeInput.value = spaceId;
    
    // Toggle active styles on cards
    document.querySelectorAll('.space-card').forEach(card => {
        card.classList.remove('active');
    });
    const selectedCard = document.querySelector(`.space-card[data-space-id="${spaceId}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
    }
    
    // Update booking form selected space display box
    const spaceDetails = spaceRates[spaceId];
    spaceDisplayBox.innerHTML = `
        <div class="active-space-info">
            <span class="active-space-name">${spaceDetails.name}</span>
            <span class="active-space-price">₦${spaceDetails.rate.toLocaleString()}/${spaceDetails.unit}</span>
        </div>
    `;
    
    // Configure inputs based on selection
    if (spaceId === 'hot_desk') {
        timeGroup.style.display = 'none';
        durationGroup.style.display = 'none';
        hotdeskInfoGroup.style.display = 'block';
        
        startTimeSelect.removeAttribute('required');
        durationSelect.removeAttribute('required');
        startTimeSelect.value = '';
        durationSelect.value = '';
    } else {
        timeGroup.style.display = 'block';
        durationGroup.style.display = 'block';
        hotdeskInfoGroup.style.display = 'none';
        
        startTimeSelect.setAttribute('required', '');
        durationSelect.setAttribute('required', '');
    }
    
    // Enable fields sequentially
    dateInput.removeAttribute('disabled');
    
    // Enable Customer Info Fields
    customerFields.forEach(el => {
        el.style.opacity = '1';
        el.style.pointerEvents = 'auto';
    });
    customerInputs.forEach(input => {
        input.removeAttribute('disabled');
    });
    
    // Reset pricing and status
    priceBox.style.display = 'none';
    hideAlert();
    disableSubmitButton();
    
    // Perform check if date is already filled
    checkAvailability();
}

/**
 * Reset Form Fields to pristine state
 */
function resetForm() {
    document.getElementById('booking-form').reset();
    currentSpace = null;
    spaceTypeInput.value = '';
    
    // Clear active card highlight
    document.querySelectorAll('.space-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Reset Space display box
    spaceDisplayBox.innerHTML = `
        <span class="placeholder-text">Please click on one of the space cards above to select a space.</span>
    `;
    
    // Disable inputs
    dateInput.setAttribute('disabled', '');
    timeGroup.style.display = 'none';
    durationGroup.style.display = 'none';
    hotdeskInfoGroup.style.display = 'none';
    
    startTimeSelect.removeAttribute('required');
    durationSelect.removeAttribute('required');
    
    // Disable customer fields
    customerFields.forEach(el => {
        el.style.opacity = '0.5';
        el.style.pointerEvents = 'none';
    });
    customerInputs.forEach(input => {
        input.setAttribute('disabled', '');
    });
    
    // Hide status and pricing boxes
    priceBox.style.display = 'none';
    hideAlert();
    disableSubmitButton();
}

/**
 * Check Space Availability via API
 */
function checkAvailability() {
    if (!currentSpace || !dateInput.value) return;
    
    const spaceId = currentSpace;
    const dateVal = dateInput.value;
    
    let url = `/api/check-availability/?space_type=${spaceId}&date=${dateVal}`;
    
    if (spaceId !== 'hot_desk') {
        const startVal = startTimeSelect.value;
        const durationVal = durationSelect.value;
        
        // Don't call API until both times are selected for rooms
        if (!startVal || !durationVal) return;
        
        url += `&start_time=${startVal}&duration=${durationVal}`;
    }
    
    // Show loading state
    hideAlert();
    disableSubmitButton();
    priceBox.style.display = 'none';
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.available) {
                // Success: Space is available
                rateValue.innerText = `₦${spaceRates[spaceId].rate.toLocaleString()}`;
                
                if (spaceId === 'hot_desk') {
                    durationValue.innerText = `1 day`;
                    totalValue.innerText = `₦${data.price.toLocaleString()}`;
                } else {
                    durationValue.innerText = `${durationSelect.value} hour(s)`;
                    totalValue.innerText = `₦${data.price.toLocaleString()}`;
                }
                
                priceBox.style.display = 'block';
                enableSubmitButton();
                showAlert('Space is available for booking!', 'success');
            } else {
                // Space is NOT available
                showAlert(data.message, 'error');
                disableSubmitButton();
            }
        })
        .catch(err => {
            showAlert('Connection error. Please try again.', 'error');
            disableSubmitButton();
        });
}

/**
 * Submit Booking details to backend
 */
function handleBookingSubmit(event) {
    event.preventDefault();
    
    if (!currentSpace || !submitBtn.dataset.enabled) return;
    
    const formData = new FormData(event.target);
    const dataObj = {};
    
    formData.forEach((value, key) => {
        dataObj[key] = value;
    });
    
    // Add duration for hot desks
    if (currentSpace === 'hot_desk') {
        dataObj['duration'] = '1';
    }
    
    // Show spinner on button
    setButtonLoadingState(true);
    hideAlert();
    
    fetch('/api/create-booking/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(dataObj)
    })
    .then(response => response.json())
    .then(data => {
        setButtonLoadingState(false);
        if (data.success) {
            // Populate Receipt Modal
            document.getElementById('receipt-ref').innerText = `#IHL-${data.booking_id}`;
            document.getElementById('receipt-space').innerText = data.details.space_name;
            document.getElementById('receipt-category').innerText = data.details.space_category;
            document.getElementById('receipt-date').innerText = data.details.date;
            document.getElementById('receipt-time').innerText = data.details.time_range;
            document.getElementById('receipt-customer').innerText = data.details.customer_name;
            document.getElementById('receipt-email').innerText = data.details.customer_email;
            document.getElementById('receipt-total').innerText = data.details.total_price;
            
            // Show success Modal
            openSuccessModal();
            
            // Reset Booking Form
            resetForm();
        } else {
            showAlert(data.message, 'error');
        }
    })
    .catch(err => {
        setButtonLoadingState(false);
        showAlert('An unexpected error occurred. Please try again.', 'error');
    });
}

// Helpers
function showAlert(message, type) {
    statusAlert.innerText = message;
    statusAlert.className = `status-alert ${type}`;
    statusAlert.style.display = 'block';
}

function hideAlert() {
    statusAlert.style.display = 'none';
}

function enableSubmitButton() {
    submitBtn.removeAttribute('disabled');
    submitBtn.dataset.enabled = "true";
}

function disableSubmitButton() {
    submitBtn.setAttribute('disabled', '');
    submitBtn.dataset.enabled = "false";
}

function setButtonLoadingState(isLoading) {
    if (isLoading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
        submitBtn.setAttribute('disabled', '');
    } else {
        btnText.style.display = 'inline-block';
        btnLoader.style.display = 'none';
        submitBtn.removeAttribute('disabled');
    }
}

function openSuccessModal() {
    successModal.classList.add('open');
}

function closeSuccessModal() {
    successModal.classList.remove('open');
}
