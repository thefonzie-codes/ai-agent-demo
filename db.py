import sqlite3
import random
import os
from datetime import datetime, timedelta
from sample_datasets.travel_company_customer_db.data import *

def generate_db(path:str, num_customers=10000):
    """Generate travel company database with sample data."""
    if os.path.exists(path):
        print("Database already exists, skipping generation")
        return

    print(f"Generating database at {path}...")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Load and execute schema from SQL file
    schema_path = 'sample_datasets/travel_company_customer_db/schema.sql'
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    
    # Convert sets to lists for random.choice
    first_names = list(FIRST_NAMES)
    last_names = list(LAST_NAMES)
    cities = list(CITIES)
    countries = list(COUNTRIES)
    languages = list(LANGUAGES)
    destinations = list(DESTINATIONS)
    package_categories = list(PACKAGE_CATEGORIES)
    package_names = list(PACKAGE_NAMES)
    payment_methods = list(PAYMENT_METHODS)
    booking_statuses = list(BOOKING_STATUS)
    payment_statuses = list(PAYMENT_STATUS)
    seasons = list(SEASONS)
    street_names = list(STREET_NAMES)
    
    # Insert customers
    print(f"Inserting {num_customers} customers...")
    used_emails = set()
    customer_data = []
    
    for i in range(num_customers):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate unique email
        email_base = f"{first_name.lower().replace(' ', '')}{last_name.lower().replace(' ', '')}"
        email = f"{email_base}@example.com"
        counter = 1
        while email in used_emails:
            email = f"{email_base}{counter}@example.com"
            counter += 1
        used_emails.add(email)
        
        # Generate phone number
        phone = f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
        
        # Generate address
        street_num = random.randint(1, 9999)
        street = random.choice(street_names)
        address = f"{street_num} {street}"
        
        city = random.choice(cities)
        country = random.choice(countries)
        
        # Generate date of birth (between 18 and 80 years old)
        years_old = random.randint(18, 80)
        dob = datetime.now() - timedelta(days=years_old*365 + random.randint(0, 365))
        dob_str = dob.strftime('%Y-%m-%d')
        
        # Generate passport number
        passport = f"{random.choice(['US', 'CA', 'UK', 'FR', 'DE', 'JP', 'AU'])}{random.randint(100000000, 999999999)}"
        
        language = random.choice(languages)
        loyalty_points = random.randint(0, 5000)
        
        # Created date (within last 2 years)
        created_days_ago = random.randint(0, 730)
        created_at = datetime.now() - timedelta(days=created_days_ago)
        created_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        customer_data.append((
            first_name, last_name, email, phone, address, city, country,
            dob_str, passport, language, loyalty_points, created_str
        ))
    
    cursor.executemany('''
        INSERT INTO customers (first_name, last_name, email, phone, address, city, country,
                              date_of_birth, passport_number, preferred_language, loyalty_points, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', customer_data)
    
    # Insert destinations
    print("Inserting destinations...")
    dest_data = []
    for dest_name in list(destinations)[:50]:
        # Extract country from destination name
        if ',' in dest_name:
            dest_country = dest_name.split(',')[-1].strip()
        else:
            dest_country = random.choice(countries)
        
        description = f"Explore the beauty and culture of {dest_name}"
        season = random.choice(seasons)
        price_per_day = round(random.uniform(50, 500), 2)
        
        dest_data.append((dest_name, dest_country, description, season, price_per_day))
    
    cursor.executemany('''
        INSERT INTO destinations (name, country, description, popular_season, avg_price_per_day)
        VALUES (?, ?, ?, ?, ?)
    ''', dest_data)
    
    num_destinations = len(dest_data)
    
    # Insert packages
    print("Inserting packages...")
    package_data = []
    pkg_names_list = list(package_names)[:50]
    
    for pkg_name in pkg_names_list:
        dest_id = random.randint(1, num_destinations)
        duration = random.choice([2, 3, 5, 7, 10, 14])
        
        # Get destination price
        cursor.execute('SELECT avg_price_per_day FROM destinations WHERE id = ?', (dest_id,))
        base_price = cursor.fetchone()[0]
        price = round(base_price * duration * random.uniform(0.8, 1.3), 2)
        
        category = random.choice(package_categories)
        max_capacity = random.randint(10, 50)
        current_bookings = random.randint(0, max_capacity)
        description = f"Enjoy a {duration}-day {category.lower()} experience"
        
        package_data.append((pkg_name, dest_id, duration, price, description, category, max_capacity, current_bookings))
    
    cursor.executemany('''
        INSERT INTO packages (name, destination_id, duration_days, price, description, category, max_capacity, current_bookings)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', package_data)
    
    num_packages = len(package_data)
    
    # Insert bookings
    num_bookings = min(num_customers * 2, 500)
    print(f"Inserting {num_bookings} bookings...")
    booking_data = []
    
    for i in range(num_bookings):
        customer_id = random.randint(1, num_customers)
        package_id = random.randint(1, num_packages)
        
        # Booking date (within last year)
        booking_days_ago = random.randint(0, 365)
        booking_date = datetime.now() - timedelta(days=booking_days_ago)
        booking_str = booking_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Travel dates (in the future or recent past)
        travel_start_offset = random.randint(-30, 90)
        travel_start = datetime.now() + timedelta(days=travel_start_offset)
        travel_start_str = travel_start.strftime('%Y-%m-%d')
        
        # Get package duration and price
        cursor.execute('SELECT duration_days, price FROM packages WHERE id = ?', (package_id,))
        duration, base_price = cursor.fetchone()
        
        travel_end = travel_start + timedelta(days=duration)
        travel_end_str = travel_end.strftime('%Y-%m-%d')
        
        num_travelers = random.randint(1, 4)
        total_price = round(base_price * num_travelers, 2)
        
        status = random.choice(booking_statuses)
        
        special_requests_list = [
            "None", "None", "None", "Window seat preferred", "Vegetarian meals",
            "Late check-in", "Wheelchair accessible", "Close to elevator",
            "Extra towels", "King bed preferred"
        ]
        special_request = random.choice(special_requests_list)
        
        booking_data.append((
            customer_id, package_id, booking_str, travel_start_str, travel_end_str,
            num_travelers, total_price, status, special_request
        ))
    
    cursor.executemany('''
        INSERT INTO bookings (customer_id, package_id, booking_date, travel_start_date, travel_end_date,
                             number_of_travelers, total_price, status, special_requests)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', booking_data)
    
    # Insert payments
    print("Inserting payments...")
    payment_data = []
    
    for booking_id in range(1, num_bookings + 1):
        # Get booking total price
        cursor.execute('SELECT total_price FROM bookings WHERE id = ?', (booking_id,))
        booking_price = cursor.fetchone()[0]
        
        # Some bookings might have multiple payments
        num_payments = random.choices([1, 2], weights=[0.8, 0.2])[0]
        
        for payment_num in range(num_payments):
            if num_payments == 1:
                amount = booking_price
            else:
                amount = round(booking_price / num_payments, 2)
            
            # Payment date
            payment_days_ago = random.randint(0, 365)
            payment_date = datetime.now() - timedelta(days=payment_days_ago)
            payment_str = payment_date.strftime('%Y-%m-%d %H:%M:%S')
            
            payment_method = random.choice(payment_methods)
            transaction_id = f"TXN{random.randint(1000000000, 9999999999)}"
            payment_status = random.choice(payment_statuses)
            
            payment_data.append((booking_id, amount, payment_str, payment_method, transaction_id, payment_status))
    
    cursor.executemany('''
        INSERT INTO payments (booking_id, amount, payment_date, payment_method, transaction_id, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', payment_data)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database generated successfully!")
    print(f"  - {num_customers} customers")
    print(f"  - {num_destinations} destinations")
    print(f"  - {num_packages} packages")
    print(f"  - {num_bookings} bookings")
    print(f"  - {len(payment_data)} payments")

def query_db(query: str) -> list:
    """Execute a query on the database."""
    if "DROP" in query.upper():
        raise Exception("DROP operations are not allowed.")
    
    try:
        conn = sqlite3.connect("./sample_datasets/travel_company_customer_db/travel_company.db")
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"Error querying database: {e}")
        return []

def delete_db(path:str):
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"File '{path}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting file '{path}': {e}")