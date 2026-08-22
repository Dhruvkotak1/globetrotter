import os
import base64
import secrets
from flask import current_app
from werkzeug.utils import secure_filename

# ==============================================================================
# 1. IMAGE & REAL-TIME WEBCAM PHOTO HANDLER
# ==============================================================================

def allowed_file(filename):
    """Check if uploaded file has an allowed image extension."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})


def save_image_from_request(file_field='avatar', base64_field='captured_photo', prefix='user'):
    """
    Saves an image from either a real-time live webcam capture (Base64 data URL)
    or a standard multipart/form-data file upload.
    
    Returns the filename stored in the static uploads directory, or None.
    """
    from flask import request
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        return None
    os.makedirs(upload_folder, exist_ok=True)
    
    # 1. Check for real-time camera capture (Base64 string)
    base64_data = request.form.get(base64_field, '').strip()
    if base64_data:
        try:
            # Handle data URL formats: "data:image/jpeg;base64,..." or "data:image/png;base64,..."
            if ',' in base64_data:
                header, encoded = base64_data.split(',', 1)
                extension = 'jpg'
                if 'png' in header:
                    extension = 'png'
                elif 'webp' in header:
                    extension = 'webp'
            else:
                encoded = base64_data
                extension = 'jpg'
                
            image_bytes = base64.b64decode(encoded)
            filename = f"{prefix}_live_{secrets.token_hex(8)}.{extension}"
            filepath = os.path.join(upload_folder, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
                
            return filename
        except Exception as e:
            current_app.logger.error(f"Error processing real-time camera photo: {e}")

    # 2. Check for standard file upload
    if file_field in request.files:
        file = request.files[file_field]
        if file and file.filename and allowed_file(file.filename):
            safe_name = secure_filename(file.filename)
            unique_name = f"{prefix}_{secrets.token_hex(8)}_{safe_name}"
            filepath = os.path.join(upload_folder, unique_name)
            file.save(filepath)
            return unique_name

    return None


# ==============================================================================
# 2. ABROAD CURRENCY CONVERTER & FOREX DATA
# ==============================================================================

# Exchange rates relative to 1 INR (Indian Rupee) as base
# (Accurate, realistic rates updated for international travel planning)
INR_EXCHANGE_RATES = {
    'INR': {'rate': 1.0, 'symbol': '₹', 'name': 'Indian Rupee', 'country': 'India', 'flag': '🇮🇳'},
    'USD': {'rate': 0.0120, 'symbol': '$', 'name': 'United States Dollar', 'country': 'United States', 'flag': '🇺🇸'},
    'EUR': {'rate': 0.0110, 'symbol': '€', 'name': 'Euro', 'country': 'European Union', 'flag': '🇪🇺'},
    'GBP': {'rate': 0.0094, 'symbol': '£', 'name': 'British Pound', 'country': 'United Kingdom', 'flag': '🇬🇧'},
    'JPY': {'rate': 1.8450, 'symbol': '¥', 'name': 'Japanese Yen', 'country': 'Japan', 'flag': '🇯🇵'},
    'AED': {'rate': 0.0440, 'symbol': 'د.إ', 'name': 'UAE Dirham', 'country': 'United Arab Emirates', 'flag': '🇦🇪'},
    'THB': {'rate': 0.4350, 'symbol': '฿', 'name': 'Thai Baht', 'country': 'Thailand', 'flag': '🇹🇭'},
    'SGD': {'rate': 0.0161, 'symbol': 'S$', 'name': 'Singapore Dollar', 'country': 'Singapore', 'flag': '🇸🇬'},
    'AUD': {'rate': 0.0182, 'symbol': 'A$', 'name': 'Australian Dollar', 'country': 'Australia', 'flag': '🇦🇺'},
    'CAD': {'rate': 0.0163, 'symbol': 'C$', 'name': 'Canadian Dollar', 'country': 'Canada', 'flag': '🇨🇦'},
    'CHF': {'rate': 0.0106, 'symbol': 'CHF', 'name': 'Swiss Franc', 'country': 'Switzerland', 'flag': '🇨🇭'},
    'IDR': {'rate': 192.50, 'symbol': 'Rp', 'name': 'Indonesian Rupiah', 'country': 'Indonesia / Bali', 'flag': '🇮🇩'},
    'VND': {'rate': 302.00, 'symbol': '₫', 'name': 'Vietnamese Dong', 'country': 'Vietnam', 'flag': '🇻🇳'},
    'MYR': {'rate': 0.0560, 'symbol': 'RM', 'name': 'Malaysian Ringgit', 'country': 'Malaysia', 'flag': '🇲🇾'},
    'SAR': {'rate': 0.0450, 'symbol': '﷼', 'name': 'Saudi Riyal', 'country': 'Saudi Arabia', 'flag': '🇸🇦'},
    'TRY': {'rate': 0.3950, 'symbol': '₺', 'name': 'Turkish Lira', 'country': 'Turkey', 'flag': '🇹🇷'},
    'NZD': {'rate': 0.0198, 'symbol': 'NZ$', 'name': 'New Zealand Dollar', 'country': 'New Zealand', 'flag': '🇳🇿'},
}

# Popular Abroad Travel Destinations for Indian Travelers with estimated daily spend ranges
POPULAR_ABROAD_DESTINATIONS = [
    {
        'country': 'United States',
        'code': 'USD',
        'symbol': '$',
        'flag': '🇺🇸',
        'cities': 'New York, San Francisco, Los Angeles',
        'rate_in_inr': 83.33,
        'daily_budget_inr': '₹12,000 - ₹25,000',
        'daily_budget_foreign': '$145 - $300',
        'tip': 'Credit cards and Forex cards widely accepted everywhere; tipping 15-20% is customary.'
    },
    {
        'country': 'Europe (Schengen Area)',
        'code': 'EUR',
        'symbol': '€',
        'flag': '🇪🇺',
        'cities': 'Paris, Rome, Barcelona, Amsterdam',
        'rate_in_inr': 90.91,
        'daily_budget_inr': '₹10,000 - ₹22,000',
        'daily_budget_foreign': '€110 - €240',
        'tip': 'Contactless cards preferred; carry small cash for public transit and street bakeries.'
    },
    {
        'country': 'United Kingdom',
        'code': 'GBP',
        'symbol': '£',
        'flag': '🇬🇧',
        'cities': 'London, Edinburgh, Manchester',
        'rate_in_inr': 106.38,
        'daily_budget_inr': '₹13,000 - ₹28,000',
        'daily_budget_foreign': '£120 - £260',
        'tip': 'Tap-to-pay is universal across London Underground and transport networks.'
    },
    {
        'country': 'Japan',
        'code': 'JPY',
        'symbol': '¥',
        'flag': '🇯🇵',
        'cities': 'Tokyo, Kyoto, Osaka',
        'rate_in_inr': 0.54,
        'daily_budget_inr': '₹8,000 - ₹18,000',
        'daily_budget_foreign': '¥15,000 - ¥33,000',
        'tip': 'Cash remains king for shrines, ramen stalls, and local trains; 7-Eleven ATMs accept Indian Forex/Debit cards.'
    },
    {
        'country': 'United Arab Emirates',
        'code': 'AED',
        'symbol': 'د.إ',
        'flag': '🇦🇪',
        'cities': 'Dubai, Abu Dhabi',
        'rate_in_inr': 22.73,
        'daily_budget_inr': '₹9,000 - ₹20,000',
        'daily_budget_foreign': 'AED 400 - AED 880',
        'tip': 'Cards accepted everywhere; duty-free shopping and taxi meters support contactless payments.'
    },
    {
        'country': 'Thailand',
        'code': 'THB',
        'symbol': '฿',
        'flag': '🇹🇭',
        'cities': 'Bangkok, Phuket, Chiang Mai',
        'rate_in_inr': 2.30,
        'daily_budget_inr': '₹4,000 - ₹9,000',
        'daily_budget_foreign': '฿1,700 - ฿3,900',
        'tip': 'Very affordable budget; carry Thai Baht cash for night markets, street food, and island boat rides.'
    },
    {
        'country': 'Singapore',
        'code': 'SGD',
        'symbol': 'S$',
        'flag': '🇸🇬',
        'cities': 'Singapore City, Sentosa',
        'rate_in_inr': 62.11,
        'daily_budget_inr': '₹9,500 - ₹21,000',
        'daily_budget_foreign': 'S$150 - S$340',
        'tip': 'Hawker centres accept QR / cash; MRT subway works directly with international contactless debit/credit cards.'
    },
    {
        'country': 'Indonesia (Bali)',
        'code': 'IDR',
        'symbol': 'Rp',
        'flag': '🇮🇩',
        'cities': 'Bali, Ubud, Seminyak, Jakarta',
        'rate_in_inr': 0.0052,
        'daily_budget_inr': '₹3,500 - ₹8,000',
        'daily_budget_foreign': 'Rp 670,000 - Rp 1,500,000',
        'tip': 'High nominal values in Rupiah; carry cash for local beach clubs, temple entries, and drivers.'
    },
    {
        'country': 'Australia',
        'code': 'AUD',
        'symbol': 'A$',
        'flag': '🇦🇺',
        'cities': 'Sydney, Melbourne, Brisbane',
        'rate_in_inr': 54.95,
        'daily_budget_inr': '₹11,000 - ₹24,000',
        'daily_budget_foreign': 'A$200 - A$440',
        'tip': 'Almost 100% cashless; card surcharges of 1-1.5% are common in restaurants.'
    },
    {
        'country': 'Switzerland',
        'code': 'CHF',
        'symbol': 'CHF',
        'flag': '🇨🇭',
        'cities': 'Zurich, Geneva, Lucerne, Interlaken',
        'rate_in_inr': 94.34,
        'daily_budget_inr': '₹15,000 - ₹32,000',
        'daily_budget_foreign': 'CHF 160 - CHF 340',
        'tip': 'Consider Swiss Travel Pass for all trains, boats, and mountain cable cars to save heavy transport expenses.'
    }
]


def convert_currency(amount, from_curr='INR', to_curr='USD'):
    """
    Converts amount from one currency to another using the exchange rate matrix.
    Returns (converted_amount, rate_multiplier).
    """
    try:
        amt = float(amount or 0.0)
    except (ValueError, TypeError):
        amt = 0.0
        
    from_curr = from_curr.upper()
    to_curr = to_curr.upper()
    
    from_info = INR_EXCHANGE_RATES.get(from_curr, INR_EXCHANGE_RATES['INR'])
    to_info = INR_EXCHANGE_RATES.get(to_curr, INR_EXCHANGE_RATES['USD'])
    
    # Convert 'from_curr' to INR first:
    # Since rates are (1 INR = X foreign_curr), 1 foreign_curr = (1 / X) INR
    if from_curr == 'INR':
        amount_in_inr = amt
    else:
        from_rate = from_info['rate']
        amount_in_inr = amt / from_rate if from_rate > 0 else 0.0
        
    # Convert INR to 'to_curr':
    if to_curr == 'INR':
        converted = amount_in_inr
        effective_rate = (1.0 / from_info['rate']) if from_curr != 'INR' and from_info['rate'] > 0 else 1.0
    else:
        to_rate = to_info['rate']
        converted = amount_in_inr * to_rate
        effective_rate = (to_rate / from_info['rate']) if from_curr != 'INR' and from_info['rate'] > 0 else to_rate
        
    return round(converted, 2), effective_rate
