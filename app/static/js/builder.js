// GlobeTrotter - Itinerary Builder Interactive Logic

let activeTripId = null;
let activeStopId = null;

function initBuilder(tripId) {
    activeTripId = tripId;
    setupDragAndDrop();
}

// ----------------------------------------------------
// Stop Management
// ----------------------------------------------------

function openAddStopModal() {
    document.getElementById('addStopForm').reset();
    openModal('addStopModal');
}

async function handleAddStopSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    const payload = {
        city_id: formData.get('city_id'),
        custom_city_name: formData.get('custom_city_name'),
        arrival_date: formData.get('arrival_date'),
        departure_date: formData.get('departure_date'),
        accommodation_name: formData.get('accommodation_name'),
        accommodation_cost: formData.get('accommodation_cost'),
        transport_mode: formData.get('transport_mode'),
        transport_cost: formData.get('transport_cost'),
        notes: formData.get('notes')
    };

    try {
        const res = await fetch(`/api/trips/${activeTripId}/stops`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            closeModal('addStopModal');
            showToast('Stop added successfully!', 'success');
            window.location.reload();
        } else {
            showToast(data.error || 'Failed to add stop', 'danger');
        }
    } catch (err) {
        console.error('Error adding stop:', err);
        showToast('Error connecting to server', 'danger');
    }
}

async function deleteStop(stopId) {
    if (!confirm('Are you sure you want to remove this stop and all its activities?')) {
        return;
    }

    try {
        const res = await fetch(`/api/stops/${stopId}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
            const el = document.getElementById(`stop-card-${stopId}`);
            if (el) el.remove();
            showToast('Stop removed successfully.', 'info');
            recalculateSummary();
        }
    } catch (err) {
        console.error('Error deleting stop:', err);
    }
}

async function moveStop(stopId, direction) {
    const container = document.getElementById('stops-list');
    const cards = Array.from(container.querySelectorAll('.builder-stop-card'));
    const currentIndex = cards.findIndex(c => c.getAttribute('data-stop-id') == stopId);
    
    if (currentIndex < 0) return;
    const targetIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (targetIndex < 0 || targetIndex >= cards.length) return;

    // Swap elements in DOM
    if (direction === 'up') {
        container.insertBefore(cards[currentIndex], cards[targetIndex]);
    } else {
        container.insertBefore(cards[targetIndex], cards[currentIndex]);
    }

    // Persist reorder to server
    const updatedOrderIds = Array.from(container.querySelectorAll('.builder-stop-card')).map(c => parseInt(c.getAttribute('data-stop-id')));
    
    try {
        await fetch(`/api/trips/${activeTripId}/stops/reorder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stop_ids: updatedOrderIds })
        });
        showToast('Stop order updated', 'info');
    } catch (err) {
        console.error('Error reordering stops:', err);
    }
}

// ----------------------------------------------------
// Activity Management
// ----------------------------------------------------

async function openAddActivityModal(stopId, cityId) {
    activeStopId = stopId;
    document.getElementById('addActivityForm').reset();
    document.getElementById('activity_stop_id').value = stopId;

    // Load city activities into suggestions dropdown
    const select = document.getElementById('catalog_activity_select');
    select.innerHTML = '<option value="">-- Choose from recommendations or enter custom --</option>';
    
    if (cityId) {
        try {
            const res = await fetch(`/api/activities/by-city/${cityId}`);
            const acts = await res.json();
            acts.forEach(act => {
                const opt = document.createElement('option');
                opt.value = act.id;
                opt.textContent = `${act.title} ($${act.estimated_cost} - ${act.category})`;
                opt.dataset.title = act.title;
                opt.dataset.cost = act.estimated_cost;
                opt.dataset.category = act.category;
                opt.dataset.desc = act.description;
                select.appendChild(opt);
            });
        } catch (err) {
            console.error('Error fetching activities:', err);
        }
    }

    openModal('addActivityModal');
}

function handleCatalogSelectChange(select) {
    const opt = select.options[select.selectedIndex];
    if (opt && opt.value) {
        document.getElementById('custom_title').value = opt.dataset.title || '';
        document.getElementById('act_cost').value = opt.dataset.cost || 0;
        document.getElementById('act_category').value = opt.dataset.category || 'Sightseeing';
        document.getElementById('custom_description').value = opt.dataset.desc || '';
    }
}

async function handleAddActivitySubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const stopId = formData.get('stop_id') || activeStopId;

    const payload = {
        activity_id: formData.get('activity_id') || null,
        custom_title: formData.get('custom_title'),
        custom_description: formData.get('custom_description'),
        day_number: formData.get('day_number'),
        time_slot: formData.get('time_slot'),
        cost: formData.get('cost'),
        category: formData.get('category'),
        notes: formData.get('notes')
    };

    try {
        const res = await fetch(`/api/stops/${stopId}/activities`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            closeModal('addActivityModal');
            showToast('Activity added to stop!', 'success');
            window.location.reload();
        } else {
            showToast(data.error || 'Failed to add activity', 'danger');
        }
    } catch (err) {
        console.error('Error adding activity:', err);
        showToast('Error connecting to server', 'danger');
    }
}

async function deleteActivity(activityId) {
    if (!confirm('Remove this activity from your itinerary?')) return;

    try {
        const res = await fetch(`/api/activities/${activityId}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
            const el = document.getElementById(`act-item-${activityId}`);
            if (el) el.remove();
            showToast('Activity removed.', 'info');
            recalculateSummary();
        }
    } catch (err) {
        console.error('Error deleting activity:', err);
    }
}

// ----------------------------------------------------
// UI Live Budget Recalculation
// ----------------------------------------------------

function recalculateSummary() {
    let total = 0;
    document.querySelectorAll('.cost-val').forEach(el => {
        const val = parseFloat(el.getAttribute('data-cost') || 0);
        total += val;
    });

    const summaryEl = document.getElementById('builder-total-cost');
    if (summaryEl) {
        summaryEl.textContent = `$${total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
}

function setupDragAndDrop() {
    // Basic hook for drag-to-reorder if enabled
}
