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
        
        print("[*] Creating demo travelers with Indian & Global profiles...")
        admin = User(
            username='admin',
            email='admin@globetrotter.com',
            first_name='Rajesh',
            last_name='Verma',
            city='Jaipur',
            country='India',
            phone='+91 98290 12345',
            bio='Lead Administrator at GlobeTrotter. Passionate about world architecture, Himalayan treks, and Rajasthan royal heritage.',
            avatar='default_avatar.png',
            is_admin=True
        )
        admin.set_password('admin123')
        
        aarav = User(
            username='aarav_travels',
            email='traveler@globetrotter.com',
            first_name='Aarav',
            last_name='Sharma',
            city='New Delhi',
            country='India',
            phone='+91 98765 43210',
            bio='Explorer & travel photographer passionate about Indian cultural heritage, Himalayan passes, and Southeast Asian street food.',
            avatar='default_avatar.png',
            is_admin=False
        )
        aarav.set_password('travel123')
        
        ananya = User(
            username='ananya_wanderer',
            email='ananya@globetrotter.com',
            first_name='Ananya',
            last_name='Iyer',
            city='Bengaluru',
            country='India',
            phone='+91 99887 66554',
            bio='Foodie, coffee aficionado, and beach enthusiast on a mission to explore 30 world destinations before turning 30.',
            avatar='default_avatar.png',
            is_admin=False
        )
        ananya.set_password('explore123')

        rohan = User(
            username='rohan_explorer',
            email='rohan@globetrotter.com',
            first_name='Rohan',
            last_name='Patel',
            city='Mumbai',
            country='India',
            phone='+91 91234 56789',
            bio='Adventure traveler, scuba diver, and budget forex wizard planning multi-city global getaways.',
            avatar='default_avatar.png',
            is_admin=False
        )
        rohan.set_password('mumbai123')
        
        db.session.add_all([admin, aarav, ananya, rohan])
        db.session.commit()
        
        print("[*] Seeding world-class Indian and Global destinations...")
        cities_data = [
            # --- INCREDIBLE INDIA DESTINATIONS ---
            {
                'name': 'Jaipur', 'country': 'India', 'region': 'India',
                'description': 'The Pink City of Rajasthan, famous for grand royal palaces, formidable hill forts, colorful bazaars, and opulent Rajput architecture.',
                'image_url': 'https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 1.8, 'popularity': 98, 'recommended_days': 3
            },
            {
                'name': 'Goa', 'country': 'India', 'region': 'India',
                'description': 'India’s coastal haven known for golden sandy beaches, vibrant shacks, Portuguese colonial heritage churches, spice farms, and sunset cruises.',
                'image_url': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.0, 'popularity': 99, 'recommended_days': 4
            },
            {
                'name': 'Varanasi', 'country': 'India', 'region': 'India',
                'description': 'The sacred spiritual heart of India on the banks of the holy Ganges river, known for ancient ghats, evening Ganga Aarti, and centuries of tradition.',
                'image_url': 'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 1.4, 'popularity': 96, 'recommended_days': 3
            },
            {
                'name': 'Ladakh (Leh)', 'country': 'India', 'region': 'India',
                'description': 'The Land of High Mountain Passes, boasting crystal azure Pangong Lake, dramatic Himalayan valleys, ancient Buddhist gompas, and stargazing.',
                'image_url': 'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.5, 'popularity': 97, 'recommended_days': 6
            },
            {
                'name': 'Kerala (Alleppey)', 'country': 'India', 'region': 'India',
                'description': 'God’s Own Country, famed for serene palm-fringed backwaters, luxury thatched houseboats, spice plantations, and Ayurvedic wellness retreats.',
                'image_url': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 1.9, 'popularity': 95, 'recommended_days': 4
            },
            {
                'name': 'Agra', 'country': 'India', 'region': 'India',
                'description': 'Home to the eternal marble masterpiece Taj Mahal, UNESCO-listed Agra Fort, and the majestic Mughal heritage of Fatehpur Sikri.',
                'image_url': 'https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 1.6, 'popularity': 98, 'recommended_days': 2
            },
            {
                'name': 'Udaipur', 'country': 'India', 'region': 'India',
                'description': 'The romantic City of Lakes in Rajasthan, celebrated for Lake Pichola, shimmering marble island palaces, royal havelis, and sunset boat rides.',
                'image_url': 'https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.2, 'popularity': 94, 'recommended_days': 3
            },
            {
                'name': 'Manali', 'country': 'India', 'region': 'India',
                'description': 'A picturesque Himalayan hill resort surrounded by snow-capped peaks, pine forests, adventure sports in Solang Valley, and Rohtang Pass.',
                'image_url': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 1.7, 'popularity': 93, 'recommended_days': 4
            },
            {
                'name': 'Rishikesh', 'country': 'India', 'region': 'India',
                'description': 'The Yoga Capital of the World along the turquoise Ganges, offering exhilarating white water rafting, cliff jumping, and spiritual ashrams.',
                'image_url': 'https://images.unsplash.com/photo-1596701062351-8c2c14d1fdd0?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 1.5, 'popularity': 92, 'recommended_days': 3
            },
            {
                'name': 'Mumbai', 'country': 'India', 'region': 'India',
                'description': 'The City of Dreams, featuring the Gateway of India, iconic Marine Drive Queen’s Necklace, Bollywood glamour, and irresistible street food.',
                'image_url': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.8, 'popularity': 95, 'recommended_days': 3
            },

            # --- POPULAR INTERNATIONAL DESTINATIONS ---
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
                'description': 'An Indonesian paradise known for forested volcanic mountains, iconic rice paddies, serene beaches, coral reefs, and yoga retreats.',
                'image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 2.0, 'popularity': 95, 'recommended_days': 6
            },
            {
                'name': 'Dubai', 'country': 'United Arab Emirates', 'region': 'Middle East',
                'description': 'A city and emirate known for luxury shopping, ultramodern architecture, Burj Khalifa vistas, and desert safaris.',
                'image_url': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 4.5, 'popularity': 93, 'recommended_days': 4
            },
            {
                'name': 'Bangkok', 'country': 'Thailand', 'region': 'Asia',
                'description': 'Thailand’s bustling capital famous for ornate shrines, lively street food stalls, river boats along the Chao Phraya, and night markets.',
                'image_url': 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=1200&q=80',
                'cost_index': 1.8, 'popularity': 94, 'recommended_days': 4
            },
            {
                'name': 'Santorini', 'country': 'Greece', 'region': 'Europe',
                'description': 'One of the Cyclades islands in the Aegean Sea, recognized for its whitewashed houses clinging to cliffs overlooking caldera sunsets.',
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
            
        print("[*] Seeding curated experiences across India and global hubs...")
        activities_data = [
            # --- JAIPUR ACTIVITIES ---
            ('Jaipur', 'Amer Fort Guided Elephant & Jeep Safari', 'Ascend the majestic hilltop Rajput fortress with intricate Sheesh Mahal mirror palace.', 'Sightseeing', 20.0, 3.0, 'https://images.unsplash.com/photo-1609946850893-6b3a0c7104b2?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Jaipur', 'Chokhi Dhani Rajasthani Cultural Dinner & Folk Dance', 'Authentic Rajasthani village experience with thali dinner, puppet shows, and fire dancers.', 'Food & Dining', 25.0, 4.0, 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80', 4.8),
            ('Jaipur', 'Hawa Mahal & Johari Bazaar Heritage Walk', 'Photograph the iconic Palace of Winds and shop for handcrafted gemstones, textiles, and jootis.', 'Culture & History', 10.0, 2.5, 'https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=600&q=80', 4.8),

            # --- GOA ACTIVITIES ---
            ('Goa', 'Scuba Diving & Dolphin Cruise at Grand Island', 'Discover vibrant coral reefs, shipwrecks, underwater marine life, and wild dolphin pods.', 'Adventure', 40.0, 5.0, 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Goa', 'Old Goa Portuguese Cathedrals & Spice Plantation Lunch', 'Explore Basilica of Bom Jesus, Se Cathedral, followed by authentic Goan fish curry at a spice farm.', 'Culture & History', 22.0, 4.0, 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=600&q=80', 4.7),
            ('Goa', 'Anjuna Beach Sunset & Curries Night Market', 'Relax with chilled coconuts and fresh seafood while listening to live acoustic music at sunset.', 'Nightlife', 15.0, 3.0, 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80', 4.8),

            # --- VARANASI ACTIVITIES ---
            ('Varanasi', 'Subah-e-Banaras Sunrise Boat Ride on Ganga', 'Row along the historic ghats at dawn as temple bells chime and morning chants echo across the river.', 'Sightseeing', 12.0, 2.0, 'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=600&q=80', 5.0),
            ('Varanasi', 'Grand Evening Ganga Aarti at Dashashwamedh Ghat', 'Witness the majestic multi-tiered brass lamp ritual and spiritual chants on the sacred riverbank.', 'Culture & History', 0.0, 1.5, 'https://images.unsplash.com/photo-1627894483216-2138af692e32?auto=format&fit=crop&w=600&q=80', 5.0),
            ('Varanasi', 'Kashi Vishwanath Temple & Sarnath Buddhist Stupa', 'Visit the golden temple of Lord Shiva and the deer park where Buddha delivered his first sermon.', 'Culture & History', 15.0, 3.5, 'https://images.unsplash.com/photo-1600100397608-f4633b49910d?auto=format&fit=crop&w=600&q=80', 4.8),

            # --- LADAKH ACTIVITIES ---
            ('Ladakh (Leh)', 'Pangong Tso Blue Lake Expedition & Camp', 'Drive through Chang La pass to the mesmerizing color-changing high altitude lake.', 'Adventure', 60.0, 8.0, 'https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?auto=format&fit=crop&w=600&q=80', 5.0),
            ('Ladakh (Leh)', 'Khardung La Pass Highest Motorable Road Trek', 'Climb up to 17,982 ft above sea level for panoramic Karakoram mountain vistas.', 'Adventure', 35.0, 4.0, 'https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Ladakh (Leh)', 'Thiksey & Hemis Monastery Morning Prayers', 'Experience peaceful Tibetan Buddhist chanting rituals and admire ancient frescoes and statues.', 'Culture & History', 10.0, 3.0, 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80', 4.8),

            # --- KERALA ACTIVITIES ---
            ('Kerala (Alleppey)', 'Private Luxury Houseboat Cruise & Traditional Feast', 'Glide along serene palm-fringed backwaters with freshly caught Karimeen fish fry lunch.', 'Leisure & Wellness', 75.0, 6.0, 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=600&q=80', 5.0),
            ('Kerala (Alleppey)', 'Munnar Tea Plantations & Eravikulam Nilgiri Trek', 'Stroll through lush rolling green tea hills and spot the endangered Nilgiri Tahr mountain goat.', 'Adventure', 25.0, 4.0, 'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=600&q=80', 4.9),

            # --- AGRA ACTIVITIES ---
            ('Agra', 'Taj Mahal Sunrise Guided Heritage Experience', 'Gaze upon the marble mausoleum illuminated in soft golden morning sunlight with expert historians.', 'Sightseeing', 20.0, 3.0, 'https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=600&q=80', 5.0),
            ('Agra', 'Agra Red Fort & Mughal Gastronomy Tour', 'Explore Shah Jahan’s palace quarters and savor rich Mughlai biryani and authentic Agra petha sweets.', 'Food & Dining', 25.0, 3.0, 'https://images.unsplash.com/photo-1585136917109-7517c24458f2?auto=format&fit=crop&w=600&q=80', 4.7),

            # --- UDAIPUR ACTIVITIES ---
            ('Udaipur', 'Lake Pichola Sunset Royal Boat Cruise', 'Cruise around Jag Mandir island palace with stunning sunset reflections across the Aravalli hills.', 'Sightseeing', 18.0, 2.0, 'https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Udaipur', 'City Palace & Dharohar Folk Dance Evening', 'Marvel at Rajasthani royal courtyards followed by vibrant lakeside cultural performances.', 'Culture & History', 20.0, 3.0, 'https://images.unsplash.com/photo-1615836245337-f5b9b2303f10?auto=format&fit=crop&w=600&q=80', 4.8),

            # --- GLOBAL ACTIVITIES ---
            ('Tokyo', 'Shibuya Sky & Crossing Golden Hour', 'Panoramic open-air observation deck looking over the bustling Shibuya crossing.', 'Sightseeing', 18.0, 2.0, 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Tokyo', 'Tsukiji Outer Market Culinary Walk', 'Sample freshly grilled wagyu beef, tamagoyaki, and pristine tuna sashimi.', 'Food & Dining', 45.0, 2.5, 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=600&q=80', 4.8),
            ('Paris', 'Eiffel Tower Summit & Champagne Toast', 'Ascend to the highest accessible observation point in Europe for sunset vistas.', 'Sightseeing', 32.0, 2.5, 'https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=600&q=80', 4.8),
            ('Rome', 'Colosseum & Roman Forum Underground Tour', 'Walk through the gladiatorial arena floor and ancient ruins of the Roman Empire.', 'Culture & History', 48.0, 3.0, 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=600&q=80', 4.9),
            ('Bali', 'Mount Batur Sunrise Volcano Trek & Hot Springs', 'Pre-dawn hike up an active volcano followed by breakfast cooked in volcanic steam.', 'Adventure', 45.0, 6.0, 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?auto=format&fit=crop&w=600&q=80', 4.9)
        ]
        
        for city_name, title, desc, cat, cost, dur, img, rating in activities_data:
            if city_name in cities:
                act = Activity(
                    city_id=cities[city_name].id,
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
        
        print("[*] Creating complete Indian and international itineraries...")
        today = date.today()
        
        # Trip 1: Royal Rajasthan Heritage (Aarav Sharma - Jaipur & Udaipur)
        trip1_start = today + timedelta(days=12)
        trip1_end = trip1_start + timedelta(days=6)
        
        trip1 = Trip(
            user_id=aarav.id,
            title='Royal Rajasthan: Forts of Jaipur & Lakes of Udaipur',
            description='A regal 7-day journey through the Pink City of Jaipur and the romantic lakes of Udaipur. Palaces, folk performances, and royal Rajasthani feasts.',
            start_date=trip1_start,
            end_date=trip1_end,
            target_budget=850.0,
            cover_image='https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80',
            visibility='public',
            share_slug='royal-rajasthan-jaipur-udaipur'
        )
        db.session.add(trip1)
        db.session.flush()
        
        stop1_1 = TripStop(
            trip_id=trip1.id,
            city_id=cities['Jaipur'].id,
            order_index=0,
            arrival_date=trip1_start,
            departure_date=trip1_start + timedelta(days=3),
            accommodation_name='ITC Rajputana Heritage Palace Jaipur',
            accommodation_cost=220.0,
            transport_mode='Train',
            transport_cost=30.0,
            notes='Vande Bharat Express from New Delhi to Jaipur'
        )
        stop1_2 = TripStop(
            trip_id=trip1.id,
            city_id=cities['Udaipur'].id,
            order_index=1,
            arrival_date=trip1_start + timedelta(days=3),
            departure_date=trip1_end,
            accommodation_name='Trident Lake Pichola Udaipur',
            accommodation_cost=260.0,
            transport_mode='Car',
            transport_cost=45.0,
            notes='Scenic drive via Chittorgarh Fort'
        )
        db.session.add_all([stop1_1, stop1_2])
        db.session.flush()

        act1 = Activity.query.filter_by(title='Amer Fort Guided Elephant & Jeep Safari').first()
        if act1:
            db.session.add(TripActivity(stop_id=stop1_1.id, activity_id=act1.id, day_number=1, activity_date=trip1_start, time_slot='09:00 AM', cost=act1.estimated_cost, category=act1.category))
            
        act2 = Activity.query.filter_by(title='Chokhi Dhani Rajasthani Cultural Dinner & Folk Dance').first()
        if act2:
            db.session.add(TripActivity(stop_id=stop1_1.id, activity_id=act2.id, day_number=2, activity_date=trip1_start + timedelta(days=1), time_slot='07:00 PM', cost=act2.estimated_cost, category=act2.category))

        act3 = Activity.query.filter_by(title='Lake Pichola Sunset Royal Boat Cruise').first()
        if act3:
            db.session.add(TripActivity(stop_id=stop1_2.id, activity_id=act3.id, day_number=4, activity_date=trip1_start + timedelta(days=3), time_slot='05:00 PM', cost=act3.estimated_cost, category=act3.category))

        db.session.add(CustomExpense(trip_id=trip1.id, title='Rajasthani Handcrafted Jootis & Souvenirs', category='Shopping & Souvenirs', amount=60.0, expense_date=trip1_start + timedelta(days=2)))
        db.session.add(CustomExpense(trip_id=trip1.id, title='Kathakali & Puppet Show Tickets', category='Activities', amount=25.0, expense_date=trip1_start + timedelta(days=4)))

        # Trip 2: Kerala God's Own Country (Ananya Iyer)
        trip2_start = today + timedelta(days=25)
        trip2_end = trip2_start + timedelta(days=5)

        trip2 = Trip(
            user_id=ananya.id,
            title='Kerala Serenade: Alleppey Backwaters & Munnar Hills',
            description='Tranquil backwater houseboats, verdant spice plantations, and misty mountain trails across God’s Own Country.',
            start_date=trip2_start,
            end_date=trip2_end,
            target_budget=650.0,
            cover_image='https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80',
            visibility='public',
            share_slug='kerala-backwaters-munnar-serenade'
        )
        db.session.add(trip2)
        db.session.flush()

        stop2_1 = TripStop(
            trip_id=trip2.id,
            city_id=cities['Kerala (Alleppey)'].id,
            order_index=0,
            arrival_date=trip2_start,
            departure_date=trip2_end,
            accommodation_name='Spice Coast Luxury Houseboat Alleppey',
            accommodation_cost=310.0,
            transport_mode='Flight',
            transport_cost=80.0
        )
        db.session.add(stop2_1)
        db.session.flush()

        act_kb = Activity.query.filter_by(title='Private Luxury Houseboat Cruise & Traditional Feast').first()
        if act_kb:
            db.session.add(TripActivity(stop_id=stop2_1.id, activity_id=act_kb.id, day_number=1, activity_date=trip2_start, time_slot='11:00 AM', cost=act_kb.estimated_cost, category=act_kb.category))

        # Trip 3: Spiritual Varanasi & Golden Triangle (Rajesh Verma)
        trip3_start = today - timedelta(days=20)
        trip3_end = today - timedelta(days=16)

        trip3 = Trip(
            user_id=admin.id,
            title='Spiritual Varanasi & Sunset Ganga Aarti Pilgrimage',
            description='Dawn boat rides past ancient ghats, evening Aarti ceremonies, and the sacred Buddhist heritage at Sarnath.',
            start_date=trip3_start,
            end_date=trip3_end,
            target_budget=450.0,
            cover_image='https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1200&q=80',
            visibility='public',
            share_slug='spiritual-varanasi-ganga-aarti'
        )
        db.session.add(trip3)
        db.session.flush()

        stop3_1 = TripStop(
            trip_id=trip3.id,
            city_id=cities['Varanasi'].id,
            order_index=0,
            arrival_date=trip3_start,
            departure_date=trip3_end,
            accommodation_name='BrijRama Palace on the Ghats',
            accommodation_cost=240.0,
            transport_mode='Flight',
            transport_cost=70.0
        )
        db.session.add(stop3_1)
        db.session.flush()

        # Wishlist & Likes
        db.session.add(SavedDestination(user_id=aarav.id, city_id=cities['Ladakh (Leh)'].id))
        db.session.add(SavedDestination(user_id=aarav.id, city_id=cities['Goa'].id))
        db.session.add(SavedDestination(user_id=ananya.id, city_id=cities['Jaipur'].id))
        db.session.add(SavedDestination(user_id=rohan.id, city_id=cities['Tokyo'].id))
        
        db.session.add(TripLike(user_id=aarav.id, trip_id=trip2.id))
        db.session.add(TripLike(user_id=admin.id, trip_id=trip1.id))
        db.session.add(TripLike(user_id=ananya.id, trip_id=trip1.id))
        db.session.add(TripLike(user_id=rohan.id, trip_id=trip3.id))

        # Seed Verified Traveler Feedback & Ratings
        fb1 = Feedback(
            user_id=aarav.id,
            name='Aarav Sharma',
            email='traveler@globetrotter.com',
            rating=5,
            category='Trip Experience',
            destination_name='Jaipur, India',
            title='Incredible Rajasthan Journey & Flawless Itinerary!',
            message='Planning our road trip between Jaipur and Udaipur was so seamless. The day-by-day activity builder and budget breakdown kept our palace hotel stays perfectly on track!',
            is_featured=True,
            created_at=datetime.utcnow() - timedelta(days=2)
        )

        fb2 = Feedback(
            user_id=ananya.id,
            name='Ananya Iyer',
            email='ananya@globetrotter.com',
            rating=5,
            category='Destination Review',
            destination_name='Kerala (Alleppey), India',
            title='Magical Sunset over Alleppey Backwaters Houseboat',
            message='The Kerala houseboat booking tips and daily budget estimator were spot on. Loved snapping live travel photos with the real-time camera feature!',
            is_featured=True,
            created_at=datetime.utcnow() - timedelta(days=5)
        )

        fb3 = Feedback(
            user_id=rohan.id,
            name='Rohan Patel',
            email='rohan@globetrotter.com',
            rating=5,
            category='Budget Planner',
            destination_name='Tokyo, Japan',
            title='Best Abroad Travel Forex & Currency Converter for Indians',
            message='Traveling abroad from Mumbai to Tokyo for the first time was daunting, but the INR to Yen currency converter and zero-forex card advice saved us thousands of rupees.',
            is_featured=True,
            created_at=datetime.utcnow() - timedelta(days=9)
        )

        fb4 = Feedback(
            user_id=admin.id,
            name='Rajesh Verma',
            email='admin@globetrotter.com',
            rating=5,
            category='Platform Feature',
            destination_name='Varanasi, India',
            title='Namaste! The Ultimate Travel Planning App for Indian Explorers',
            message='GlobeTrotter combines the vibrant charm of Indian heritage destinations with world-class international travel tools. The real-time camera capture is brilliant.',
            is_featured=True,
            created_at=datetime.utcnow() - timedelta(days=12)
        )

        db.session.add_all([fb1, fb2, fb3, fb4])
        
        db.session.commit()
        print("[SUCCESS] Database successfully seeded with Indian & world-class travel data!")
        print("[INFO] Test Accounts:")
        print("   - Admin:    admin@globetrotter.com    / admin123  (Rajesh Verma)")
        print("   - Traveler: traveler@globetrotter.com / travel123 (Aarav Sharma)")
        print("   - Ananya:   ananya@globetrotter.com   / explore123")
        print("   - Rohan:    rohan@globetrotter.com    / mumbai123")

if __name__ == '__main__':
    seed_database()
