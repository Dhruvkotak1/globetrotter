from datetime import date, datetime, timedelta
import secrets
from app import create_app
from app.extensions import db
from app.models import User, City, Activity, Trip, TripStop, TripActivity, CustomExpense, SavedDestination, TripLike, Feedback

app = create_app()

def seed_database():
    with app.app_context():
        print("[*] Initializing and dropping existing tables...")
        db.drop_all()
        db.create_all()
        
        print("[*] Creating demo users...")
        admin = User(
            username='admin',
            email='admin@globetrotter.com',
            first_name='Admin',
            last_name='Traveler',
            city='San Francisco',
            country='United States',
            phone='+1 (415) 555-0100',
            bio='Lead Administrator at GlobeTrotter. Passionate about world architecture and mountain treks.',
            is_admin=True
        )
        admin.set_password('admin123')
        
        traveler = User(
            username='alex_travels',
            email='traveler@globetrotter.com',
            first_name='Alex',
            last_name='Morgan',
            city='London',
            country='United Kingdom',
            phone='+44 20 7946 0912',
            bio='Digital nomad & photographer exploring the hidden gems of Europe and East Asia.',
            is_admin=False
        )
        traveler.set_password('travel123')
        
        sarah = User(
            username='sarah_wanderlust',
            email='sarah@globetrotter.com',
            first_name='Sarah',
            last_name='Jenkins',
            city='Sydney',
            country='Australia',
            phone='+61 2 9876 5432',
            bio='Foodie, coffee aficionado, and beach enthusiast on a mission to visit 50 countries before 30.',
            is_admin=False
        )
        sarah.set_password('explore123')
        
        db.session.add_all([admin, traveler, sarah])
        db.session.commit()
        
        print("[*] Seeding world-class destinations...")
        cities_data = [
            {
                'name': 'Tokyo', 'country': 'Japan', 'region': 'Asia',
                'description': 'A vibrant metropolis blending ultra-modern neon skyscrapers with historic shrines, world-renowned gastronomy, and tranquil gardens.',
                'image_url': 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 3.8, 'popularity': 98, 'recommended_days': 5
            },
            {
                'name': 'Kyoto', 'country': 'Japan', 'region': 'Asia',
                'description': 'The cultural heart of Japan, famed for classical Buddhist temples, gardens, imperial palaces, Shinto shrines and traditional wooden houses.',
                'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 3.2, 'popularity': 92, 'recommended_days': 3
            },
            {
                'name': 'Paris', 'country': 'France', 'region': 'Europe',
                'description': 'The City of Light captivates travelers with monumental landmarks, haute cuisine, chic boutiques, and legendary art museums.',
                'image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 4.2, 'popularity': 99, 'recommended_days': 4
            },
            {
                'name': 'Rome', 'country': 'Italy', 'region': 'Europe',
                'description': 'An open-air museum of nearly 3,000 years of globally influential art, architecture, ancient Colosseum ruins, and authentic Italian dining.',
                'image_url': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 3.5, 'popularity': 96, 'recommended_days': 4
            },
            {
                'name': 'Barcelona', 'country': 'Spain', 'region': 'Europe',
                'description': 'A seaside city celebrated for Antoni Gaudí’s architectural wonders, vibrant tapas bars, Mediterranean beaches, and lively street life.',
                'image_url': 'https://images.unsplash.com/photo-1539037116277-4db20889f2d4?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 3.2, 'popularity': 94, 'recommended_days': 4
            },
            {
                'name': 'New York City', 'country': 'United States', 'region': 'Americas',
                'description': 'The city that never sleeps, featuring iconic skylines, Central Park strolls, Broadway theatre, and incredible cultural diversity.',
                'image_url': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 4.8, 'popularity': 97, 'recommended_days': 5
            },
            {
                'name': 'Bali', 'country': 'Indonesia', 'region': 'Asia',
                'description': 'An Indonesian paradise known for its forested volcanic mountains, iconic rice paddies, serene beaches, coral reefs, and yoga retreats.',
                'image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.0, 'popularity': 95, 'recommended_days': 6
            },
            {
                'name': 'London', 'country': 'United Kingdom', 'region': 'Europe',
                'description': 'A 21st-century city with history stretching to Roman times, housing Big Ben, the Tower of London, world-class West End shows and royal parks.',
                'image_url': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 4.4, 'popularity': 96, 'recommended_days': 4
            },
            {
                'name': 'Cairo', 'country': 'Egypt', 'region': 'Africa',
                'description': 'Egypt’s sprawling capital on the Nile river, home to the Giza Pyramid complex, the Great Sphinx, and the treasure-filled Grand Egyptian Museum.',
                'image_url': 'https://images.unsplash.com/photo-1572252009286-268acec5ca0a?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.2, 'popularity': 89, 'recommended_days': 3
            },
            {
                'name': 'Dubai', 'country': 'United Arab Emirates', 'region': 'Middle East',
                'description': 'A city and emirate known for luxury shopping, ultramodern architecture, Burj Khalifa vistas, and a lively nightlife scene.',
                'image_url': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 4.5, 'popularity': 93, 'recommended_days': 4
            },
            {
                'name': 'Sydney', 'country': 'Australia', 'region': 'Oceania',
                'description': 'Australia’s glittering coastal metropolis featuring the iconic Sydney Opera House, Harbour Bridge, Bondi Beach surfing, and sunny shores.',
                'image_url': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 4.0, 'popularity': 91, 'recommended_days': 4
            },
            {
                'name': 'Cape Town', 'country': 'South Africa', 'region': 'Africa',
                'description': 'A port city on South Africa’s southwest coast, beneath towering Table Mountain, renowned for dramatic ocean views, penguins, and wine valleys.',
                'image_url': 'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.5, 'popularity': 88, 'recommended_days': 5
            },
            {
                'name': 'Amsterdam', 'country': 'Netherlands', 'region': 'Europe',
                'description': 'The Netherlands’ capital famous for picturesque canal networks, historic gabled houses, Van Gogh Museum, and vibrant cycling culture.',
                'image_url': 'https://images.unsplash.com/photo-1512470876302-972faa2aa9a4?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 3.7, 'popularity': 93, 'recommended_days': 3
            },
            {
                'name': 'Bangkok', 'country': 'Thailand', 'region': 'Asia',
                'description': 'Thailand’s bustling capital famous for ornate shrines, lively street food stalls, river boats along the Chao Phraya, and bustling night markets.',
                'image_url': 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 1.8, 'popularity': 94, 'recommended_days': 4
            },
            {
                'name': 'Rio de Janeiro', 'country': 'Brazil', 'region': 'Americas',
                'description': 'A huge seaside city in Brazil, famed for its Copacabana and Ipanema beaches, Christ the Redeemer statue, and Sugarloaf Mountain.',
                'image_url': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.4, 'popularity': 90, 'recommended_days': 4
            },
            {
                'name': 'Santorini', 'country': 'Greece', 'region': 'Europe',
                'description': 'One of the Cyclades islands in the Aegean Sea, recognized for its whitewashed, cubiform houses clinging to cliffs overlooking caldera sunsets.',
                'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 4.1, 'popularity': 95, 'recommended_days': 3
            }
        ]
        
        cities = {}
        for cdata in cities_data:
            city = City(**cdata)
            db.session.add(city)
            db.session.flush()
            cities[cdata['name']] = city
            
        print("[*] Seeding curated activities & experiences...")
        activities_data = [
            # Tokyo
            ('Tokyo', 'Shibuya Sky & Crossing Golden Hour', 'Panoramic open-air observation deck looking over the bustling Shibuya crossing.', 'Sightseeing', 18.0, 2.0, 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Tokyo', 'Tsukiji Outer Market Culinary Walk', 'Sample freshly grilled wagyu beef, tamagoyaki, and pristine tuna sashimi from market artisans.', 'Food & Dining', 45.0, 2.5, 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=600&q=80', 4.8),
            ('Tokyo', 'teamLab Planets Digital Art Immersion', 'Sensory museum walking through water and immersive light crystal infinity rooms.', 'Culture & History', 28.0, 2.5, 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Tokyo', 'Asakusa Senso-ji Temple & Kimono Rental', 'Walk through the Thunder Gate and explore Tokyo’s oldest and most revered temple complex.', 'Culture & History', 35.0, 3.0, 'https://images.unsplash.com/photo-1492571350019-22de08371fd3?auto=format&fit=crop&w=600&q=80', 4.7),

            # Kyoto
            ('Kyoto', 'Fushimi Inari Torii Gates Sunrise Trek', 'Hike along thousands of vermilion torii gates winding up sacred Mount Inari.', 'Adventure', 0.0, 3.0, 'https://images.unsplash.com/photo-1478436127897-769e00d0c71e?auto=format&fit=crop&w=600&q=80', 5.0),
            ('Kyoto', 'Arashiyama Bamboo Grove & Monkey Park', 'Towering bamboo stalks swaying in the breeze, followed by panoramic mountain views.', 'Sightseeing', 8.0, 2.5, 'https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=600&q=80', 4.8),
            ('Kyoto', 'Authentic Matcha Tea Ceremony in Gion', 'Traditional Zen tea preparation guided by a Kyoto tea master in a historic machiya.', 'Culture & History', 40.0, 1.5, 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=600&q=80', 4.9),

            # Paris
            ('Paris', 'Eiffel Tower Summit & Champagne Toast', 'Ascend to the highest accessible observation point in Europe for breathtaking sunset vistas.', 'Sightseeing', 32.0, 2.5, 'https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=600&q=80', 4.8),
            ('Paris', 'Louvre Masterpieces Guided Tour', 'Skip-the-line journey through the Mona Lisa, Venus de Milo, and Winged Victory.', 'Culture & History', 55.0, 3.0, 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Paris', 'Seine River Gourmet Sunset Cruise', 'Gliding past illuminated historic bridges and Notre-Dame while enjoying French pastries.', 'Leisure & Wellness', 65.0, 2.0, 'https://images.unsplash.com/photo-1509439581779-6298f75bf6e5?auto=format&fit=crop&w=600&q=80', 4.7),

            # Rome
            ('Rome', 'Colosseum & Roman Forum Underground Tour', 'Walk through the gladiatorial arena floor and ancient ruins of the Roman Empire.', 'Culture & History', 48.0, 3.0, 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Rome', 'Trastevere Secret Food & Wine Safari', 'Sample authentic cacio e pepe, supplì, Roman pizza, and artisanal gelato.', 'Food & Dining', 75.0, 3.5, 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=600&q=80', 5.0),
            ('Rome', 'Vatican Museums & Sistine Chapel Tour', 'Admire Michelangelo’s ceiling frescoes and the stunning St. Peter’s Basilica.', 'Culture & History', 52.0, 3.5, 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=600&q=80', 4.8),

            # Barcelona
            ('Barcelona', 'Sagrada Família Fast-Track & Towers', 'Gaze upon Antoni Gaudí’s breathtaking nature-inspired stained glass basilica.', 'Sightseeing', 36.0, 2.0, 'https://images.unsplash.com/photo-1583779457094-0cef55c065f4?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Barcelona', 'Park Güell Architectural Walk', 'Vibrant mosaic salamanders and panoramic vistas overlooking Barcelona to the sea.', 'Sightseeing', 14.0, 2.0, 'https://images.unsplash.com/photo-1523531294919-4bcd7c65e216?auto=format&fit=crop&w=600&q=80', 4.7),
            ('Barcelona', 'Gothic Quarter Tapas & Sangria Tour', 'Hop through century-old bodegas tasting jamón ibérico and Catalan cheeses.', 'Food & Dining', 50.0, 3.0, 'https://images.unsplash.com/photo-1515443961218-a51367888e4b?auto=format&fit=crop&w=600&q=80', 4.8),

            # New York
            ('New York City', 'Summit One Vanderbilt Skydeck', 'Multi-sensory reflective art installations suspended over midtown Manhattan.', 'Sightseeing', 42.0, 2.0, 'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=600&q=80', 4.9),
            ('New York City', 'Broadway Musical Night', 'World-class musical theatre performance in the heart of Times Square.', 'Nightlife', 110.0, 3.0, 'https://images.unsplash.com/photo-1508997449629-303059a039c0?auto=format&fit=crop&w=600&q=80', 4.9),
            ('New York City', 'Central Park Bike Tour & Picnic', 'Cycle past Strawberry Fields, Bethesda Fountain, and Bow Bridge.', 'Leisure & Wellness', 25.0, 2.5, 'https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=600&q=80', 4.7),

            # Bali
            ('Bali', 'Mount Batur Sunrise Volcano Trek & Hot Springs', 'Pre-dawn hike up an active volcano followed by breakfast cooked in volcanic steam.', 'Adventure', 45.0, 6.0, 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Bali', 'Ubud Sacred Monkey Forest & Waterfall Trek', 'Encounter playful macaques amongst mossy temple ruins and bathe in Tegenungan falls.', 'Adventure', 15.0, 3.5, 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=600&q=80', 4.8),
            ('Bali', 'Traditional Balinese Spa & Flower Bath', 'Herbal body scrub, deep tissue massage, and relaxing soak in frangipani blossoms.', 'Leisure & Wellness', 35.0, 2.0, 'https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=600&q=80', 5.0),

            # Cairo
            ('Cairo', 'Great Pyramids of Giza & Camel Ride', 'Stand before Khufu’s Wonder of the Ancient World and ride camels across the desert dunes.', 'Culture & History', 40.0, 4.0, 'https://images.unsplash.com/photo-1503177112275-5de592a11b64?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Cairo', 'Khan el-Khalili Bazaar Souk Exploration', 'Navigate medieval vaulted alleys filled with spices, brass lamps, and Egyptian perfumes.', 'Food & Dining', 10.0, 2.5, 'https://images.unsplash.com/photo-1572252009286-268acec5ca0a?auto=format&fit=crop&w=600&q=80', 4.6),

            # London
            ('London', 'Tower of London & Crown Jewels', 'Discover royal history, the White Tower, and sparkling sovereign regalia.', 'Culture & History', 38.0, 3.0, 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=600&q=80', 4.8),
            ('London', 'Traditional Afternoon Tea at The Ritz', 'Warm scones with clotted cream, finger sandwiches, and fine artisan teas.', 'Food & Dining', 75.0, 2.0, 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=600&q=80', 4.7),

            # Santorini
            ('Santorini', 'Oia Sunset Catamaran Sailing & Snorkeling', 'Sail around the volcano, swim in volcanic hot springs, and watch the legendary Oia sunset.', 'Adventure', 120.0, 5.0, 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=600&q=80', 5.0),
            ('Santorini', 'Volcanic Winery Tasting & Greek Mezze', 'Sample crisp Assyrtiko wines paired with Santorini tomato fritters and fava puree.', 'Food & Dining', 55.0, 2.5, 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=600&q=80', 4.9)
        ]
        
        for cname, title, desc, cat, cost, dur, img, rating in activities_data:
            if cname in cities:
                act = Activity(
                    city_id=cities[cname].id,
                    title=title,
                    description=desc,
                    category=cat,
                    estimated_cost=cost,
                    duration_hours=dur,
                    image_url=img,
                    rating=rating
                )
                db.session.add(act)
                
        db.session.commit()
        
        print("[*] Creating complete multi-city demo trips...")
        
        # Trip 1: Japan Golden Route (Alex Morgan - Ongoing / Upcoming)
        today = date.today()
        trip1_start = today + timedelta(days=10)
        trip1_end = trip1_start + timedelta(days=7)
        
        trip1 = Trip(
            user_id=traveler.id,
            title='Wonders of Japan: Tokyo & Kyoto Explorer',
            description='A curated 8-day expedition through futuristic Tokyo and historic Kyoto, experiencing Shinto shrines, Michelin ramen, and bullet trains.',
            start_date=trip1_start,
            end_date=trip1_end,
            target_budget=2800.0,
            cover_image='https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80',
            visibility='public',
            share_slug='japan-golden-route-2026'
        )
        db.session.add(trip1)
        db.session.flush()
        
        # Stop 1: Tokyo
        stop1_1 = TripStop(
            trip_id=trip1.id,
            city_id=cities['Tokyo'].id,
            order_index=0,
            arrival_date=trip1_start,
            departure_date=trip1_start + timedelta(days=4),
            accommodation_name='Hotel Gracery Shinjuku',
            accommodation_cost=550.0,
            transport_mode='Flight',
            transport_cost=650.0,
            notes='Check-in after 3 PM. Take Narita Express train.'
        )
        db.session.add(stop1_1)
        db.session.flush()
        
        # Stop 2: Kyoto
        stop1_2 = TripStop(
            trip_id=trip1.id,
            city_id=cities['Kyoto'].id,
            order_index=1,
            arrival_date=trip1_start + timedelta(days=4),
            departure_date=trip1_end,
            accommodation_name='Kyoto Machiya Heritage Ryokan',
            accommodation_cost=420.0,
            transport_mode='Train / Shinkansen',
            transport_cost=110.0,
            notes='Nozomi bullet train from Tokyo Station track 14.'
        )
        db.session.add(stop1_2)
        db.session.flush()
        
        # Activities for Trip 1
        act1 = Activity.query.filter_by(title='Shibuya Sky & Crossing Golden Hour').first()
        if act1:
            db.session.add(TripActivity(stop_id=stop1_1.id, activity_id=act1.id, day_number=1, activity_date=trip1_start, time_slot='Evening', cost=act1.estimated_cost, category=act1.category))
            
        act2 = Activity.query.filter_by(title='Tsukiji Outer Market Culinary Walk').first()
        if act2:
            db.session.add(TripActivity(stop_id=stop1_1.id, activity_id=act2.id, day_number=2, activity_date=trip1_start + timedelta(days=1), time_slot='Morning', cost=act2.estimated_cost, category=act2.category))
            
        act3 = Activity.query.filter_by(title='teamLab Planets Digital Art Immersion').first()
        if act3:
            db.session.add(TripActivity(stop_id=stop1_1.id, activity_id=act3.id, day_number=3, activity_date=trip1_start + timedelta(days=2), time_slot='Afternoon', cost=act3.estimated_cost, category=act3.category))
            
        act4 = Activity.query.filter_by(title='Fushimi Inari Torii Gates Sunrise Trek').first()
        if act4:
            db.session.add(TripActivity(stop_id=stop1_2.id, activity_id=act4.id, day_number=5, activity_date=trip1_start + timedelta(days=4), time_slot='Morning', cost=act4.estimated_cost, category=act4.category))
            
        act5 = Activity.query.filter_by(title='Authentic Matcha Tea Ceremony in Gion').first()
        if act5:
            db.session.add(TripActivity(stop_id=stop1_2.id, activity_id=act5.id, day_number=6, activity_date=trip1_start + timedelta(days=5), time_slot='Afternoon', cost=act5.estimated_cost, category=act5.category))
            
        # Custom expenses for Trip 1
        db.session.add(CustomExpense(trip_id=trip1.id, title='Japan Rail Pass (7-Day)', category='Transport & Flights', amount=240.0, expense_date=trip1_start, notes='Unlimited bullet trains'))
        db.session.add(CustomExpense(trip_id=trip1.id, title='Pocket WiFi Rental', category='Other', amount=45.0, expense_date=trip1_start))
        
        # Trip 2: European Grand Tour (Sarah Jenkins - Public Community)
        trip2_start = today + timedelta(days=30)
        trip2_end = trip2_start + timedelta(days=9)
        
        trip2 = Trip(
            user_id=sarah.id,
            title='Classic European Summer: Paris, Rome & Barcelona',
            description='Ten unforgettable days traveling across three iconic European cultural capitals. Architecture, fine wine, world heritage museums and sunset beaches.',
            start_date=trip2_start,
            end_date=trip2_end,
            target_budget=3400.0,
            cover_image='https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80',
            visibility='public',
            share_slug='europe-paris-rome-barcelona'
        )
        db.session.add(trip2)
        db.session.flush()
        
        stop2_1 = TripStop(
            trip_id=trip2.id,
            city_id=cities['Paris'].id,
            order_index=0,
            arrival_date=trip2_start,
            departure_date=trip2_start + timedelta(days=3),
            accommodation_name='Hôtel Le Marais Paris',
            accommodation_cost=480.0,
            transport_mode='Flight',
            transport_cost=550.0
        )
        stop2_2 = TripStop(
            trip_id=trip2.id,
            city_id=cities['Rome'].id,
            order_index=1,
            arrival_date=trip2_start + timedelta(days=3),
            departure_date=trip2_start + timedelta(days=6),
            accommodation_name='Navona Residenza Boutique',
            accommodation_cost=410.0,
            transport_mode='Flight',
            transport_cost=95.0
        )
        stop2_3 = TripStop(
            trip_id=trip2.id,
            city_id=cities['Barcelona'].id,
            order_index=2,
            arrival_date=trip2_start + timedelta(days=6),
            departure_date=trip2_end,
            accommodation_name='Hotel Arts Barcelona Waterfront',
            accommodation_cost=520.0,
            transport_mode='Flight',
            transport_cost=80.0
        )
        db.session.add_all([stop2_1, stop2_2, stop2_3])
        db.session.flush()
        
        # Trip 3: Bali Retreat (Admin User - Past Trip)
        trip3_start = today - timedelta(days=45)
        trip3_end = today - timedelta(days=39)
        
        trip3 = Trip(
            user_id=admin.id,
            title='Tropical Wellness & Volcanic Hikes in Bali',
            description='A rejuvenating tropical escape through Ubud and Seminyak featuring volcano sunrise treks, flower baths, and healthy organic cafes.',
            start_date=trip3_start,
            end_date=trip3_end,
            target_budget=1600.0,
            cover_image='https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1200&q=80',
            visibility='public',
            share_slug='bali-tropical-wellness'
        )
        db.session.add(trip3)
        db.session.flush()
        
        stop3_1 = TripStop(
            trip_id=trip3.id,
            city_id=cities['Bali'].id,
            order_index=0,
            arrival_date=trip3_start,
            departure_date=trip3_end,
            accommodation_name='Komaneka at Monkey Forest Ubud',
            accommodation_cost=650.0,
            transport_mode='Flight',
            transport_cost=700.0
        )
        db.session.add(stop3_1)
        db.session.flush()
        
        # Wishlist & Likes
        db.session.add(SavedDestination(user_id=traveler.id, city_id=cities['Santorini'].id))
        db.session.add(SavedDestination(user_id=traveler.id, city_id=cities['Rome'].id))
        db.session.add(SavedDestination(user_id=sarah.id, city_id=cities['Tokyo'].id))
        
        db.session.add(TripLike(user_id=traveler.id, trip_id=trip2.id))
        db.session.add(TripLike(user_id=admin.id, trip_id=trip2.id))
        db.session.add(TripLike(user_id=sarah.id, trip_id=trip1.id))

        # Seed Verified Traveler Feedback & Ratings
        fb1 = Feedback(
            user_id=traveler.id,
            name='Alex Morgan',
            email='traveler@globetrotter.com',
            rating=5,
            category='Trip Experience',
            destination_name='Tokyo, Japan',
            title='Flawless 10-Day Multi-City Japan Itinerary!',
            message='Planning our journey between Tokyo and Kyoto was unbelievably smooth. The budget breakdown accurately forecasted our train and ramen expenses in Yen!',
            is_featured=True,
            created_at=datetime.utcnow() - timedelta(days=3)
        )

        fb2 = Feedback(
            user_id=sarah.id,
            name='Sarah Jenkins',
            email='sarah@globetrotter.com',
            rating=5,
            category='Destination Review',
            destination_name='Bali, Indonesia',
            title='Mesmerizing Ubud Waterfalls & Sunsets',
            message='The activity builder helped us schedule sunrise volcano treks and sacred temple visits without any guesswork. The currency converter saved us lots of Rupiah math!',
            is_featured=True,
            created_at=datetime.utcnow() - timedelta(days=7)
        )

        fb3 = Feedback(
            user_id=None,
            name='Rohan Patel',
            email='rohan.travels@gmail.com',
            rating=5,
            category='Budget Planner',
            destination_name='Paris, France',
            title='Best Abroad Travel Forex & Budget Tool for Indians',
            message='Traveling abroad from Mumbai to Europe for the first time was daunting, but the INR to EUR converter and real-time expense logger kept our entire honeymoon strictly on budget.',
            is_featured=True,
            created_at=datetime.utcnow() - timedelta(days=10)
        )

        fb4 = Feedback(
            user_id=admin.id,
            name='Admin Traveler',
            email='admin@globetrotter.com',
            rating=4,
            category='Platform Feature',
            destination_name='Rome, Italy',
            title='Real-time Camera Capture is a Game Changer',
            message='Love how quickly I can snap live travel photos right from my browser and attach them to my itinerary reviews.',
            is_featured=False,
            created_at=datetime.utcnow() - timedelta(days=14)
        )

        db.session.add_all([fb1, fb2, fb3, fb4])
        
        db.session.commit()
        print("[SUCCESS] Database successfully seeded with rich travel data!")
        print("[INFO] Test Accounts:")
        print("   - Admin:    admin@globetrotter.com    / admin123")
        print("   - Traveler: traveler@globetrotter.com / travel123")
        print("   - Sarah:    sarah@globetrotter.com    / explore123")

if __name__ == '__main__':
    seed_database()
