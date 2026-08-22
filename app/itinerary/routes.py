from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Trip, TripStop, TripActivity, City, Activity
from app.itinerary import itinerary_bp

@itinerary_bp.route('/trips/<int:trip_id>/builder')
@login_required
def builder(trip_id):
    """Screen 5: Itinerary Builder Screen"""
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    cities = City.query.order_by(City.name.asc()).all()
    return render_template('itinerary/builder.html', trip=trip, cities=cities)


@itinerary_bp.route('/trips/<int:trip_id>/itinerary')
def view_itinerary(trip_id):
    """Screen 6: Itinerary View Screen (Day-wise grouped view with physical activity + expense)"""
    trip = Trip.query.get_or_404(trip_id)
    
    # Check accessibility: if private, must be owner or admin
    if trip.visibility == 'private' and (not current_user.is_authenticated or (trip.user_id != current_user.id and not current_user.is_admin)):
        flash('This itinerary is private.', 'warning')
        return redirect(url_for('trips.my_trips') if current_user.is_authenticated else url_for('auth.login'))
        
    # Group activities and stops by day
    # Create day-by-day structure from start_date to end_date
    total_days = trip.duration_days
    days_data = []
    
    for day_idx in range(total_days):
        current_day_date = trip.start_date + timedelta(days=day_idx)
        day_number = day_idx + 1
        
        # Find stops active on this day
        active_stops = []
        for stop in trip.stops:
            if stop.arrival_date <= current_day_date <= stop.departure_date:
                active_stops.append(stop)
                
        # Find activities for this day
        day_activities = []
        for stop in trip.stops:
            for act in stop.activities:
                # Match by explicit date or day_number
                if act.activity_date == current_day_date or act.day_number == day_number:
                    day_activities.append({
                        'activity': act,
                        'stop': stop
                    })
                    
        # Calculate daily expense
        day_expense = sum(item['activity'].cost or 0.0 for item in day_activities)
        # If this is the arrival day for a stop, include accommodation/transport
        for st in active_stops:
            if st.arrival_date == current_day_date:
                day_expense += (st.transport_cost or 0.0)
            # Add proportional accommodation cost per night
            if st.duration_days > 0:
                day_expense += round((st.accommodation_cost or 0.0) / st.duration_days, 2)
                
        days_data.append({
            'day_number': day_number,
            'date': current_day_date,
            'active_stops': active_stops,
            'activities': day_activities,
            'estimated_expense': round(day_expense, 2)
        })
        
    return render_template(
        'itinerary/view.html',
        trip=trip,
        days_data=days_data,
        total_days=total_days
    )


@itinerary_bp.route('/trips/<int:trip_id>/calendar')
def trip_calendar(trip_id):
    """Screen 10: Trip Calendar / Timeline Screen"""
    trip = Trip.query.get_or_404(trip_id)
    
    if trip.visibility == 'private' and (not current_user.is_authenticated or (trip.user_id != current_user.id and not current_user.is_admin)):
        flash('This itinerary is private.', 'warning')
        return redirect(url_for('trips.my_trips') if current_user.is_authenticated else url_for('auth.login'))
        
    stops_data = [stop.to_dict() for stop in trip.stops]
    return render_template('itinerary/calendar.html', trip=trip, stops_data=stops_data)


@itinerary_bp.route('/cities')
def city_search():
    """Screen 7: City Search Screen"""
    query = request.args.get('q', '').strip()
    region_filter = request.args.get('region', '').strip()
    cost_filter = request.args.get('cost', '').strip() # e.g., '1', '2', '3', '4', '5'
    sort_by = request.args.get('sort', 'popularity') # popularity, name, cost_asc, cost_desc
    
    cities_query = City.query
    
    if query:
        cities_query = cities_query.filter(City.name.ilike(f'%{query}%') | City.country.ilike(f'%{query}%'))
        
    if region_filter and region_filter.lower() != 'all':
        cities_query = cities_query.filter(City.region == region_filter)
        
    if cost_filter:
        try:
            cost_val = float(cost_filter)
            cities_query = cities_query.filter(City.cost_index <= cost_val)
        except ValueError:
            pass
            
    if sort_by == 'name':
        cities_query = cities_query.order_by(City.name.asc())
    elif sort_by == 'cost_asc':
        cities_query = cities_query.order_by(City.cost_index.asc())
    elif sort_by == 'cost_desc':
        cities_query = cities_query.order_by(City.cost_index.desc())
    else:
        cities_query = cities_query.order_by(City.popularity.desc())
        
    cities = cities_query.all()
    
    # Get distinct regions for filter dropdown
    regions = db.session.query(City.region).distinct().all()
    regions_list = [r[0] for r in regions if r[0]]
    
    # User's trips (if logged in) so they can quickly "Add to Trip"
    user_trips = []
    if current_user.is_authenticated:
        user_trips = current_user.trips.filter(Trip.end_date >= date.today()).order_by(Trip.start_date.asc()).all()
        
    return render_template(
        'itinerary/cities.html',
        cities=cities,
        regions=regions_list,
        selected_region=region_filter,
        selected_cost=cost_filter,
        sort_by=sort_by,
        search_query=query,
        user_trips=user_trips
    )


@itinerary_bp.route('/activities')
def activity_search():
    """Screen 8: Activity Search Screen"""
    query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    city_id_filter = request.args.get('city_id', '').strip()
    max_cost = request.args.get('max_cost', '').strip()
    max_duration = request.args.get('max_duration', '').strip()
    sort_by = request.args.get('sort', 'rating') # rating, cost_asc, cost_desc, duration
    
    act_query = Activity.query
    
    if query:
        act_query = act_query.filter(Activity.title.ilike(f'%{query}%') | Activity.description.ilike(f'%{query}%'))
        
    if category_filter and category_filter.lower() != 'all':
        act_query = act_query.filter(Activity.category == category_filter)
        
    if city_id_filter:
        try:
            c_id = int(city_id_filter)
            act_query = act_query.filter(Activity.city_id == c_id)
        except ValueError:
            pass
            
    if max_cost:
        try:
            mc = float(max_cost)
            act_query = act_query.filter(Activity.estimated_cost <= mc)
        except ValueError:
            pass
            
    if max_duration:
        try:
            md = float(max_duration)
            act_query = act_query.filter(Activity.duration_hours <= md)
        except ValueError:
            pass
            
    if sort_by == 'cost_asc':
        act_query = act_query.order_by(Activity.estimated_cost.asc())
    elif sort_by == 'cost_desc':
        act_query = act_query.order_by(Activity.estimated_cost.desc())
    elif sort_by == 'duration':
        act_query = act_query.order_by(Activity.duration_hours.asc())
    else:
        act_query = act_query.order_by(Activity.rating.desc())
        
    activities = act_query.all()
    all_cities = City.query.order_by(City.name.asc()).all()
    
    # Categories list
    categories = ['Sightseeing', 'Food & Dining', 'Adventure', 'Culture & History', 'Leisure & Wellness', 'Transport', 'Nightlife']
    
    # User's active trips for quick add
    user_trips = []
    if current_user.is_authenticated:
        user_trips = current_user.trips.filter(Trip.end_date >= date.today()).order_by(Trip.start_date.asc()).all()
        
    return render_template(
        'itinerary/activities.html',
        activities=activities,
        all_cities=all_cities,
        categories=categories,
        selected_category=category_filter,
        selected_city=city_id_filter,
        max_cost=max_cost,
        max_duration=max_duration,
        sort_by=sort_by,
        search_query=query,
        user_trips=user_trips
    )


# ==========================================
# REST API Endpoints for Interactive Builder
# ==========================================

@itinerary_bp.route('/api/trips/<int:trip_id>/stops', methods=['POST'])
@login_required
def add_stop(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json() or request.form
    city_id = data.get('city_id')
    custom_city_name = data.get('custom_city_name', '').strip()
    arrival_str = data.get('arrival_date')
    departure_str = data.get('departure_date')
    accommodation_name = data.get('accommodation_name', '').strip()
    accommodation_cost = float(data.get('accommodation_cost', 0) or 0)
    transport_mode = data.get('transport_mode', 'Flight')
    transport_cost = float(data.get('transport_cost', 0) or 0)
    notes = data.get('notes', '').strip()
    
    try:
        arrival_date = datetime.strptime(arrival_str, '%Y-%m-%d').date() if arrival_str else trip.start_date
        departure_date = datetime.strptime(departure_str, '%Y-%m-%d').date() if departure_str else trip.end_date
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
        
    # Calculate next order index
    next_order = len(trip.stops)
    
    stop = TripStop(
        trip_id=trip.id,
        city_id=int(city_id) if city_id else None,
        custom_city_name=custom_city_name,
        order_index=next_order,
        arrival_date=arrival_date,
        departure_date=departure_date,
        accommodation_name=accommodation_name,
        accommodation_cost=accommodation_cost,
        transport_mode=transport_mode,
        transport_cost=transport_cost,
        notes=notes
    )
    db.session.add(stop)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Stop "{stop.display_city_name}" added.',
        'stop': stop.to_dict()
    })


@itinerary_bp.route('/api/stops/<int:stop_id>', methods=['PUT', 'POST'])
@login_required
def update_stop(stop_id):
    stop = TripStop.query.get_or_404(stop_id)
    if stop.trip.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json() or request.form
    if 'city_id' in data:
        stop.city_id = int(data['city_id']) if data['city_id'] else None
    if 'custom_city_name' in data:
        stop.custom_city_name = data['custom_city_name']
    if 'arrival_date' in data and data['arrival_date']:
        stop.arrival_date = datetime.strptime(data['arrival_date'], '%Y-%m-%d').date()
    if 'departure_date' in data and data['departure_date']:
        stop.departure_date = datetime.strptime(data['departure_date'], '%Y-%m-%d').date()
    if 'accommodation_name' in data:
        stop.accommodation_name = data['accommodation_name']
    if 'accommodation_cost' in data:
        stop.accommodation_cost = float(data['accommodation_cost'] or 0)
    if 'transport_mode' in data:
        stop.transport_mode = data['transport_mode']
    if 'transport_cost' in data:
        stop.transport_cost = float(data['transport_cost'] or 0)
    if 'notes' in data:
        stop.notes = data['notes']
        
    db.session.commit()
    return jsonify({'success': True, 'stop': stop.to_dict()})


@itinerary_bp.route('/api/stops/<int:stop_id>', methods=['DELETE'])
@login_required
def delete_stop(stop_id):
    stop = TripStop.query.get_or_404(stop_id)
    if stop.trip.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    trip_id = stop.trip_id
    db.session.delete(stop)
    db.session.commit()
    
    # Re-sequence remaining stops
    remaining = TripStop.query.filter_by(trip_id=trip_id).order_by(TripStop.order_index.asc()).all()
    for idx, s in enumerate(remaining):
        s.order_index = idx
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Stop deleted successfully.'})


@itinerary_bp.route('/api/trips/<int:trip_id>/stops/reorder', methods=['POST'])
@login_required
def reorder_stops(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json() or {}
    stop_ids = data.get('stop_ids', [])
    
    for idx, s_id in enumerate(stop_ids):
        stop = TripStop.query.filter_by(id=s_id, trip_id=trip.id).first()
        if stop:
            stop.order_index = idx
            
    db.session.commit()
    return jsonify({'success': True, 'message': 'Stops reordered successfully.'})


@itinerary_bp.route('/api/stops/<int:stop_id>/activities', methods=['POST'])
@login_required
def add_activity_to_stop(stop_id):
    stop = TripStop.query.get_or_404(stop_id)
    if stop.trip.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json() or request.form
    activity_id = data.get('activity_id')
    custom_title = data.get('custom_title', '').strip()
    custom_desc = data.get('custom_description', '').strip()
    day_number = int(data.get('day_number', 1) or 1)
    time_slot = data.get('time_slot', 'Morning')
    cost = float(data.get('cost', 0) or 0)
    category = data.get('category', 'Sightseeing')
    notes = data.get('notes', '').strip()
    act_date_str = data.get('activity_date')
    
    act_date = None
    if act_date_str:
        try:
            act_date = datetime.strptime(act_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    elif stop.arrival_date:
        act_date = stop.arrival_date + timedelta(days=max(0, day_number - 1))
        
    # If activity_id is provided, populate defaults if title/cost not entered
    if activity_id:
        catalog_act = Activity.query.get(int(activity_id))
        if catalog_act:
            if not custom_title:
                custom_title = catalog_act.title
            if not cost:
                cost = catalog_act.estimated_cost
            if not category:
                category = catalog_act.category
                
    next_order = len(stop.activities)
    
    trip_act = TripActivity(
        stop_id=stop.id,
        activity_id=int(activity_id) if activity_id else None,
        custom_title=custom_title,
        custom_description=custom_desc,
        day_number=day_number,
        activity_date=act_date,
        time_slot=time_slot,
        cost=cost,
        category=category,
        order_index=next_order,
        notes=notes
    )
    db.session.add(trip_act)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Activity "{trip_act.display_title}" added.',
        'activity': trip_act.to_dict()
    })


@itinerary_bp.route('/api/activities/<int:activity_id>', methods=['PUT', 'POST'])
@login_required
def update_activity(activity_id):
    act = TripActivity.query.get_or_404(activity_id)
    if act.stop.trip.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json() or request.form
    if 'custom_title' in data:
        act.custom_title = data['custom_title']
    if 'custom_description' in data:
        act.custom_description = data['custom_description']
    if 'day_number' in data:
        act.day_number = int(data['day_number'] or 1)
    if 'time_slot' in data:
        act.time_slot = data['time_slot']
    if 'cost' in data:
        act.cost = float(data['cost'] or 0)
    if 'category' in data:
        act.category = data['category']
    if 'notes' in data:
        act.notes = data['notes']
    if 'activity_date' in data and data['activity_date']:
        try:
            act.activity_date = datetime.strptime(data['activity_date'], '%Y-%m-%d').date()
        except ValueError:
            pass
            
    db.session.commit()
    return jsonify({'success': True, 'activity': act.to_dict()})


@itinerary_bp.route('/api/activities/<int:activity_id>', methods=['DELETE'])
@login_required
def delete_activity(activity_id):
    act = TripActivity.query.get_or_404(activity_id)
    if act.stop.trip.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    db.session.delete(act)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Activity removed.'})


@itinerary_bp.route('/api/stops/<int:stop_id>/activities/reorder', methods=['POST'])
@login_required
def reorder_activities(stop_id):
    stop = TripStop.query.get_or_404(stop_id)
    if stop.trip.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json() or {}
    act_ids = data.get('activity_ids', [])
    
    for idx, a_id in enumerate(act_ids):
        act = TripActivity.query.filter_by(id=a_id, stop_id=stop.id).first()
        if act:
            act.order_index = idx
            
    db.session.commit()
    return jsonify({'success': True, 'message': 'Activities reordered.'})


@itinerary_bp.route('/api/cities/search')
def api_search_cities():
    q = request.args.get('q', '').strip()
    cities = City.query.filter(City.name.ilike(f'%{q}%') | City.country.ilike(f'%{q}%')).limit(10).all()
    return jsonify([c.to_dict() for c in cities])


@itinerary_bp.route('/api/activities/by-city/<int:city_id>')
def api_activities_by_city(city_id):
    acts = Activity.query.filter_by(city_id=city_id).order_by(Activity.rating.desc()).all()
    return jsonify([a.to_dict() for a in acts])
