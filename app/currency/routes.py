from flask import render_template, request, jsonify
from app.currency import currency_bp
from app.utils import INR_EXCHANGE_RATES, POPULAR_ABROAD_DESTINATIONS, convert_currency

@currency_bp.route('/currency-converter')
def converter():
    """
    Abroad Travel Currency Converter Screen.
    Allows travelers from India or anywhere in the world to convert travel budgets,
    compare daily travel costs across major international destinations, and calculate forex.
    """
    from_curr = request.args.get('from', 'INR').upper()
    to_curr = request.args.get('to', 'USD').upper()
    amount_str = request.args.get('amount', '50000')
    
    try:
        amount = float(amount_str)
    except (ValueError, TypeError):
        amount = 50000.0
        
    converted_amount, rate = convert_currency(amount, from_curr, to_curr)
    
    # Calculate quick conversions for popular destination matrix
    destination_conversions = []
    for dest in POPULAR_ABROAD_DESTINATIONS:
        dest_code = dest['code']
        conv_val, _ = convert_currency(amount, from_curr, dest_code)
        destination_conversions.append({
            'country': dest['country'],
            'code': dest_code,
            'symbol': dest['symbol'],
            'flag': dest['flag'],
            'cities': dest['cities'],
            'converted_amount': conv_val,
            'daily_budget_inr': dest['daily_budget_inr'],
            'daily_budget_foreign': dest['daily_budget_foreign'],
            'tip': dest['tip'],
            'rate_in_inr': dest['rate_in_inr']
        })
        
    return render_template(
        'currency/converter.html',
        from_curr=from_curr,
        to_curr=to_curr,
        amount=amount,
        converted_amount=converted_amount,
        rate=rate,
        rates_data=INR_EXCHANGE_RATES,
        popular_destinations=destination_conversions
    )


@currency_bp.route('/api/currency/convert', methods=['GET', 'POST'])
def api_convert():
    """API endpoint for instantaneous currency conversion without page reload."""
    if request.method == 'POST':
        data = request.get_json() or request.form
    else:
        data = request.args
        
    amount = data.get('amount', 1000)
    from_curr = data.get('from', 'INR')
    to_curr = data.get('to', 'USD')
    
    converted, rate = convert_currency(amount, from_curr, to_curr)
    
    from_info = INR_EXCHANGE_RATES.get(from_curr.upper(), {'symbol': ''})
    to_info = INR_EXCHANGE_RATES.get(to_curr.upper(), {'symbol': ''})
    
    return jsonify({
        'success': True,
        'amount': float(amount or 0),
        'from': from_curr.upper(),
        'from_symbol': from_info.get('symbol', ''),
        'to': to_curr.upper(),
        'to_symbol': to_info.get('symbol', ''),
        'converted': converted,
        'rate': rate,
        'formatted': f"{to_info.get('symbol', '')}{converted:,.2f}"
    })


@currency_bp.route('/api/currency/rates')
def api_rates():
    """API endpoint returning all current foreign currency exchange rates."""
    return jsonify({
        'success': True,
        'base': 'INR',
        'rates': INR_EXCHANGE_RATES
    })
