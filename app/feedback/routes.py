from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user
from sqlalchemy import func
from app.extensions import db
from app.models import Feedback, City
from app.utils import save_image_from_request
from app.feedback import feedback_bp

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def index():
    """
    Feedback & Reviews Hub.
    Allows travelers to rate their experiences (1-5 stars), upload live camera or file photos,
    and view community reviews with rating analytics.
    """
    if request.method == 'POST':
        # Retrieve form data
        if current_user.is_authenticated:
            name = current_user.full_name or current_user.username
            email = current_user.email
            user_id = current_user.id
        else:
            name = request.form.get('name', '').strip() or 'Anonymous Traveler'
            email = request.form.get('email', '').strip() or 'traveler@globetrotter.com'
            user_id = None
            
        rating_val = request.form.get('rating', '5')
        category = request.form.get('category', 'Trip Experience')
        destination_name = request.form.get('destination_name', '').strip()
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validations
        if not title or not message:
            flash('Please provide both a title and feedback description.', 'danger')
            return redirect(url_for('feedback.index'))
            
        try:
            rating = int(rating_val)
            rating = max(1, min(5, rating)) # clamp between 1 and 5
        except (ValueError, TypeError):
            rating = 5
            
        # Process live camera capture (Base64) or uploaded image file
        photo_filename = save_image_from_request(
            file_field='photo',
            base64_field='captured_photo',
            prefix='feedback'
        )
        
        new_feedback = Feedback(
            user_id=user_id,
            name=name,
            email=email,
            rating=rating,
            category=category,
            destination_name=destination_name,
            title=title,
            message=message,
            photo=photo_filename,
            is_featured=True if rating >= 4 else False
        )
        
        db.session.add(new_feedback)
        db.session.commit()
        
        flash(f'Thank you for your {rating}★ rating! Your feedback has been shared with the community.', 'success')
        return redirect(url_for('feedback.index'))
        
    # GET request: Display feedback list with filters and rating stats
    rating_filter = request.args.get('rating', '')
    category_filter = request.args.get('category', '')
    
    query = Feedback.query
    
    if rating_filter and rating_filter.isdigit():
        query = query.filter(Feedback.rating == int(rating_filter))
    if category_filter:
        query = query.filter(Feedback.category == category_filter)
        
    feedbacks = query.order_by(Feedback.created_at.desc()).all()
    
    # Calculate overall rating metrics
    all_feedbacks = Feedback.query.all()
    total_count = len(all_feedbacks)
    
    if total_count > 0:
        avg_rating = round(sum(f.rating for f in all_feedbacks) / total_count, 1)
    else:
        avg_rating = 5.0
        
    # Rating breakdown counts (5, 4, 3, 2, 1)
    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for f in all_feedbacks:
        r = f.rating if f.rating in rating_counts else 5
        rating_counts[r] += 1
        
    rating_percentages = {}
    for r in range(1, 6):
        pct = round((rating_counts[r] / total_count * 100), 1) if total_count > 0 else 0
        rating_percentages[r] = pct
        
    cities = City.query.order_by(City.name.asc()).all()
    
    return render_template(
        'feedback/index.html',
        feedbacks=feedbacks,
        total_count=total_count,
        avg_rating=avg_rating,
        rating_counts=rating_counts,
        rating_percentages=rating_percentages,
        selected_rating=rating_filter,
        selected_category=category_filter,
        cities=cities
    )


@feedback_bp.route('/api/feedback', methods=['GET'])
def api_feedbacks():
    """API endpoint to retrieve latest feedbacks as JSON."""
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(20).all()
    return jsonify({
        'success': True,
        'feedbacks': [f.to_dict() for f in feedbacks]
    })
