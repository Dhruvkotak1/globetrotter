from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Trip, CustomExpense
from app.budget import budget_bp

@budget_bp.route('/trips/<int:trip_id>/budget')
def view_budget(trip_id):
    """Screen 9: Trip Budget & Cost Breakdown Screen"""
    trip = Trip.query.get_or_404(trip_id)
    
    if trip.visibility == 'private' and (not current_user.is_authenticated or (trip.user_id != current_user.id and not current_user.is_admin)):
        flash('This itinerary budget is private.', 'warning')
        return redirect(url_for('trips.my_trips') if current_user.is_authenticated else url_for('auth.login'))
        
    breakdown = trip.breakdown_by_category
    total_cost = trip.total_cost
    per_day_cost = trip.per_day_cost
    is_overbudget = trip.is_overbudget
    budget_pct = trip.budget_percentage
    
    # Calculate daily spend data for the bar chart
    total_days = trip.duration_days
    day_labels = []
    day_costs = []
    
    for day_idx in range(total_days):
        current_day_date = trip.start_date + timedelta(days=day_idx)
        day_labels.append(f"Day {day_idx + 1} ({current_day_date.strftime('%b %d')})")
        
        day_total = 0.0
        # Stop transports on arrival date
        for stop in trip.stops:
            if stop.arrival_date == current_day_date:
                day_total += (stop.transport_cost or 0.0)
            if stop.arrival_date <= current_day_date <= stop.departure_date and stop.duration_days > 0:
                day_total += ((stop.accommodation_cost or 0.0) / stop.duration_days)
            for act in stop.activities:
                if act.activity_date == current_day_date or act.day_number == (day_idx + 1):
                    day_total += (act.cost or 0.0)
                    
        for exp in trip.custom_expenses:
            if exp.expense_date == current_day_date:
                day_total += (exp.amount or 0.0)
                
        day_costs.append(round(day_total, 2))
        
    return render_template(
        'budget/breakdown.html',
        trip=trip,
        breakdown=breakdown,
        total_cost=total_cost,
        per_day_cost=per_day_cost,
        is_overbudget=is_overbudget,
        budget_pct=budget_pct,
        day_labels=day_labels,
        day_costs=day_costs
    )


@budget_bp.route('/api/trips/<int:trip_id>/budget-data')
def get_budget_data(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    breakdown = trip.breakdown_by_category
    
    total_days = trip.duration_days
    day_labels = []
    day_costs = []
    
    for day_idx in range(total_days):
        current_day_date = trip.start_date + timedelta(days=day_idx)
        day_labels.append(f"Day {day_idx + 1}")
        
        day_total = 0.0
        for stop in trip.stops:
            if stop.arrival_date == current_day_date:
                day_total += (stop.transport_cost or 0.0)
            if stop.arrival_date <= current_day_date <= stop.departure_date and stop.duration_days > 0:
                day_total += ((stop.accommodation_cost or 0.0) / stop.duration_days)
            for act in stop.activities:
                if act.activity_date == current_day_date or act.day_number == (day_idx + 1):
                    day_total += (act.cost or 0.0)
                    
        for exp in trip.custom_expenses:
            if exp.expense_date == current_day_date:
                day_total += (exp.amount or 0.0)
                
        day_costs.append(round(day_total, 2))
        
    return jsonify({
        'categories': {
            'labels': ['Transport', 'Accommodation/Stay', 'Activities', 'Meals & Dining', 'Other / Custom'],
            'data': [breakdown['transport'], breakdown['stay'], breakdown['activities'], breakdown['meals'], breakdown['other']]
        },
        'daily': {
            'labels': day_labels,
            'data': day_costs
        },
        'total_cost': trip.total_cost,
        'target_budget': trip.target_budget,
        'is_overbudget': trip.is_overbudget,
        'per_day_cost': trip.per_day_cost
    })


@budget_bp.route('/api/trips/<int:trip_id>/expenses', methods=['POST'])
@login_required
def add_expense(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not current_user.is_admin:
        if request.is_json:
            return jsonify({'error': 'Unauthorized'}), 403
        flash('You do not have permission to modify this trip.', 'warning')
        return redirect(url_for('budget.view_budget', trip_id=trip.id))
        
    data = request.get_json(silent=True) or request.form
    title = (data.get('title') or '').strip()
    category = data.get('category', 'Other')
    amount_val = data.get('amount', 0)
    date_str = data.get('expense_date')
    notes = (data.get('notes') or '').strip()
    
    if not title:
        if request.is_json:
            return jsonify({'error': 'Expense title is required'}), 400
        flash('Expense title is required.', 'danger')
        return redirect(url_for('budget.view_budget', trip_id=trip.id))
        
    try:
        amount = float(amount_val)
    except (ValueError, TypeError):
        if request.is_json:
            return jsonify({'error': 'Invalid amount entered'}), 400
        flash('Please enter a valid expense amount.', 'danger')
        return redirect(url_for('budget.view_budget', trip_id=trip.id))
        
    exp_date = None
    if date_str:
        try:
            exp_date = datetime.strptime(str(date_str).strip(), '%Y-%m-%d').date()
        except ValueError:
            exp_date = trip.start_date
    else:
        exp_date = trip.start_date
            
    expense = CustomExpense(
        trip_id=trip.id,
        title=title,
        category=category,
        amount=amount,
        expense_date=exp_date,
        notes=notes
    )
    db.session.add(expense)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'expense': expense.to_dict(), 'total_cost': trip.total_cost})
    else:
        from app.utils import format_user_currency
        formatted_cost = format_user_currency(amount)
        flash(f'Expense "{title}" ({formatted_cost}) added successfully.', 'success')
        return redirect(url_for('budget.view_budget', trip_id=trip.id))


@budget_bp.route('/api/expenses/<int:expense_id>', methods=['DELETE', 'POST'])
@login_required
def delete_expense(expense_id):
    exp = CustomExpense.query.get_or_404(expense_id)
    trip = exp.trip
    if trip.user_id != current_user.id and not current_user.is_admin:
        if request.is_json or request.method == 'DELETE':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('You do not have permission to modify this expense.', 'warning')
        return redirect(url_for('budget.view_budget', trip_id=trip.id))
        
    db.session.delete(exp)
    db.session.commit()
    
    if request.is_json or request.method == 'DELETE':
        return jsonify({'success': True, 'message': 'Expense deleted', 'total_cost': trip.total_cost})
    else:
        flash('Custom expense removed successfully.', 'info')
        return redirect(url_for('budget.view_budget', trip_id=trip.id))
