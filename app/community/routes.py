from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Trip, TripLike, City
from app.community import community_bp

@community_bp.route('/community')
def index():
    """Screen 10 (Mockup) / Community Hub: Public gallery of shared itineraries"""
    query = request.args.get('q', '').strip()
    duration_filter = request.args.get('duration', '') # e.g., '1-3', '4-7', '8+'
    budget_filter = request.args.get('budget', '') # 'budget' (<1000), 'mid' (1000-3000), 'luxury' (>3000)
    sort_by = request.args.get('sort', 'likes') # 'likes', 'newest', 'duration'
    
    trips_query = Trip.query.filter_by(visibility='public')
    
    if query:
        trips_query = trips_query.filter(Trip.title.ilike(f'%{query}%') | Trip.description.ilike(f'%{query}%'))
        
    all_public = trips_query.all()
    
    # Filter in python for complex properties
    filtered = []
    for t in all_public:
        # Duration filter
        if duration_filter == '1-3' and not (1 <= t.duration_days <= 3):
            continue
        elif duration_filter == '4-7' and not (4 <= t.duration_days <= 7):
            continue
        elif duration_filter == '8+' and not (t.duration_days >= 8):
            continue
            
        # Budget filter
        if budget_filter == 'budget' and not (t.total_cost < 1000):
            continue
        elif budget_filter == 'mid' and not (1000 <= t.total_cost <= 3000):
            continue
        elif budget_filter == 'luxury' and not (t.total_cost > 3000):
            continue
            
        filtered.append(t)
        
    if sort_by == 'newest':
        filtered.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == 'duration':
        filtered.sort(key=lambda x: x.duration_days, reverse=True)
    else: # 'likes'
        filtered.sort(key=lambda x: len(x.likes), reverse=True)
        
    # Get user's liked trip IDs
    user_liked_ids = set()
    if current_user.is_authenticated:
        user_liked_ids = {like.trip_id for like in current_user.likes}
        
    return render_template(
        'community/index.html',
        trips=filtered,
        user_liked_ids=user_liked_ids,
        search_query=query,
        duration_filter=duration_filter,
        budget_filter=budget_filter,
        sort_by=sort_by
    )


@community_bp.route('/trip/shared/<string:share_slug>')
def view_shared(share_slug):
    """Screen 11: Shared/Public Itinerary View Screen"""
    trip = Trip.query.filter_by(share_slug=share_slug).first()
    
    # Fallback: if user passes an integer ID and the trip is public
    if not trip and share_slug.isdigit():
        trip = Trip.query.get(int(share_slug))
        
    if not trip:
        abort(404)
        
    # If trip is private, only owner or admin can view
    if trip.visibility == 'private' and (not current_user.is_authenticated or (trip.user_id != current_user.id and not current_user.is_admin)):
        flash('This shared itinerary is private or has expired.', 'warning')
        return redirect(url_for('community.index'))
        
    is_liked = False
    if current_user.is_authenticated:
        is_liked = TripLike.query.filter_by(user_id=current_user.id, trip_id=trip.id).first() is not None
        
    return render_template(
        'community/view_shared.html',
        trip=trip,
        is_liked=is_liked,
        share_url=request.base_url
    )


@community_bp.route('/community/trips/<int:trip_id>/like', methods=['POST'])
@login_required
def toggle_like(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    existing_like = TripLike.query.filter_by(user_id=current_user.id, trip_id=trip.id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        new_like = TripLike(user_id=current_user.id, trip_id=trip.id)
        db.session.add(new_like)
        db.session.commit()
        liked = True
        
    like_count = TripLike.query.filter_by(trip_id=trip.id).count()
    return jsonify({'success': True, 'liked': liked, 'like_count': like_count})
