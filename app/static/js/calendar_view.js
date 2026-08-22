// GlobeTrotter - Interactive Monthly Calendar

function initTripCalendar(tripStartDate, tripEndDate, stopsData) {
    let currentMonth = new Date(tripStartDate);
    renderCalendar(currentMonth, tripStartDate, tripEndDate, stopsData);

    const prevBtn = document.getElementById('cal-prev-month');
    const nextBtn = document.getElementById('cal-next-month');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentMonth.setMonth(currentMonth.getMonth() - 1);
            renderCalendar(currentMonth, tripStartDate, tripEndDate, stopsData);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentMonth.setMonth(currentMonth.getMonth() + 1);
            renderCalendar(currentMonth, tripStartDate, tripEndDate, stopsData);
        });
    }
}

function renderCalendar(viewDate, tripStart, tripEnd, stopsData) {
    const monthTitle = document.getElementById('cal-month-title');
    const grid = document.getElementById('cal-days-grid');
    if (!grid || !monthTitle) return;

    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();

    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    monthTitle.textContent = `${monthNames[month]} ${year}`;

    // Get first day of month & days in month
    const firstDayIndex = new Date(year, month, 1).getDay(); // 0 is Sunday
    const totalDaysInMonth = new Date(year, month + 1, 0).getDate();
    const prevMonthDays = new Date(year, month, 0).getDate();

    grid.innerHTML = '';

    const startTripDate = new Date(tripStart);
    const endTripDate = new Date(tripEnd);
    startTripDate.setHours(0, 0, 0, 0);
    endTripDate.setHours(0, 0, 0, 0);

    // 1. Previous month padded days
    for (let i = firstDayIndex - 1; i >= 0; i--) {
        const cell = document.createElement('div');
        cell.className = 'calendar-cell';
        cell.style.opacity = '0.35';
        cell.innerHTML = `<span class="calendar-cell-date">${prevMonthDays - i}</span>`;
        grid.appendChild(cell);
    }

    // 2. Current month days
    for (let day = 1; day <= totalDaysInMonth; day++) {
        const thisDate = new Date(year, month, day);
        thisDate.setHours(0, 0, 0, 0);
        
        const cell = document.createElement('div');
        cell.className = 'calendar-cell';
        
        const isTripDay = thisDate >= startTripDate && thisDate <= endTripDate;
        if (isTripDay) {
            cell.classList.add('trip-day');
        }

        let dayContent = `<span class="calendar-cell-date">${day}</span>`;

        // Check if any stops/activities occur on this date
        const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        
        if (stopsData && stopsData.length) {
            stopsData.forEach(stop => {
                const arr = new Date(stop.arrival_date);
                const dep = new Date(stop.departure_date);
                arr.setHours(0, 0, 0, 0);
                dep.setHours(0, 0, 0, 0);

                if (thisDate >= arr && thisDate <= dep) {
                    dayContent += `<div class="calendar-event-pill" title="${stop.display_city_name}">${stop.display_city_name}</div>`;
                }

                if (stop.activities) {
                    stop.activities.forEach(act => {
                        if (act.activity_date === dateString) {
                            dayContent += `<div class="calendar-event-pill" style="background:#06b6d4;" title="${act.title}">${act.title}</div>`;
                        }
                    });
                }
            });
        }

        cell.innerHTML = dayContent;
        cell.style.cursor = 'pointer';
        cell.addEventListener('click', () => {
            showDayDetails(dateString, isTripDay, stopsData);
        });

        grid.appendChild(cell);
    }
}

function showDayDetails(dateString, isTripDay, stopsData) {
    if (!isTripDay) {
        showToast(`Date ${dateString} is outside the scheduled trip period.`, 'info');
        return;
    }

    // Show day modal or jump
    showToast(`Viewing schedule for ${dateString}`, 'info');
}
