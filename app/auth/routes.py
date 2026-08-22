import os
import secrets
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import User, Trip, City, SavedDestination
from app.utils import save_image_from_request, allowed_file
from app.auth import auth_bp

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('trips.my_trips'))
        
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip() # can be email or username
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        if not identifier or not password:
            flash('Please enter both your email/username and password.', 'danger')
            return render_template('auth/login.html')
            
        user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid email/username or password. Please try again.', 'danger')
            return render_template('auth/login.html')
            
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.first_name or user.username}!', 'success')
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('trips.my_trips')
        return redirect(next_page)
        
    return render_template('auth/login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('trips.my_trips'))
        
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Validations
        if not username or not email or not password:
            flash('Username, email, and password are required.', 'danger')
            return render_template('auth/signup.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/signup.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/signup.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'warning')
            return render_template('auth/signup.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please log in.', 'warning')
            return render_template('auth/signup.html')
            
        # Avatar handling (live camera snapshot or file upload)
        uploaded_avatar = save_image_from_request(
            file_field='avatar',
            base64_field='captured_avatar',
            prefix=f"user_{username}"
        )
        avatar_filename = uploaded_avatar or 'default_avatar.png'
                
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            city=city,
            country=country,
            bio=bio,
            avatar=avatar_filename
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Account created successfully! Welcome to GlobeTrotter!', 'success')
        return redirect(url_for('trips.my_trips'))
        
    return render_template('auth/signup.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('trips.my_trips'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            # For demonstration in local app, we display the direct reset link
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f'Password reset link generated! For demo purposes, you can use: {reset_url}', 'info')
            return render_template('auth/forgot_password.html', reset_url=reset_url)
        else:
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
            return render_template('auth/forgot_password.html')
            
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('trips.my_trips'))
        
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/reset_password.html', token=token)
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)
            
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        
        flash('Your password has been successfully reset. Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', '').strip()
        current_user.last_name = request.form.get('last_name', '').strip()
        current_user.email = request.form.get('email', '').strip().lower()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.city = request.form.get('city', '').strip()
        current_user.country = request.form.get('country', '').strip()
        # Preferred currency update
        currency_pref = request.form.get('preferred_currency', 'INR').strip().upper()
        if currency_pref:
            current_user.preferred_currency = currency_pref

        # Handle avatar change (live camera snapshot or file upload)
        new_avatar = save_image_from_request(
            file_field='avatar',
            base64_field='captured_avatar',
            prefix=f"user_{current_user.username}"
        )
        if new_avatar:
            current_user.avatar = new_avatar
                
        db.session.commit()
        flash('Profile settings and currency preference updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
        
    # Get user trips segregated into preplanned and completed/previous
    all_trips = current_user.trips.order_by(Trip.start_date.asc()).all()
    preplanned_trips = [t for t in all_trips if t.status in ('upcoming', 'ongoing')]
    previous_trips = [t for t in all_trips if t.status == 'completed']
    saved_dests = [sd.city for sd in current_user.saved_destinations.all() if sd.city]
    
    return render_template(
        'auth/profile.html',
        user=current_user,
        preplanned_trips=preplanned_trips,
        previous_trips=previous_trips,
        saved_dests=saved_dests
    )


@auth_bp.route('/set-currency', methods=['POST', 'GET'])
def set_currency():
    """Quickly switch preferred display currency for active session and user profile."""
    from flask import session
    currency_code = (request.values.get('currency') or request.values.get('currency_code') or 'INR').strip().upper()
    
    if current_user.is_authenticated:
        current_user.preferred_currency = currency_code
        db.session.commit()
        
    session['preferred_currency'] = currency_code
    
    next_url = request.values.get('next') or request.referrer or url_for('index')
    if request.is_json:
        return jsonify({'success': True, 'currency': currency_code})
    flash(f'Display currency updated to {currency_code}.', 'info')
    return redirect(next_url)


@auth_bp.route('/profile/delete-account', methods=['POST'])
@login_required
def delete_account():
    confirmation = request.form.get('confirm_delete', '').strip()
    if confirmation.lower() != 'delete':
        flash('Please type "DELETE" to confirm account deletion.', 'warning')
        return redirect(url_for('auth.profile'))
        
    user = current_user
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Your account and all associated trips have been permanently deleted.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/api/save-destination/<int:city_id>', methods=['POST'])
@login_required
def toggle_save_destination(city_id):
    city = City.query.get_or_404(city_id)
    existing = SavedDestination.query.filter_by(user_id=current_user.id, city_id=city_id).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'saved': False, 'message': f'{city.name} removed from your saved places.'})
    else:
        new_save = SavedDestination(user_id=current_user.id, city_id=city_id)
        db.session.add(new_save)
        db.session.commit()
        return jsonify({'saved': True, 'message': f'{city.name} added to your saved places!'})
