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
        
        # VERIFY: Get destination price and ensure destination exists
        cursor.execute('SELECT avg_price_per_day FROM destinations WHERE id = ?', (dest_id,))
        result = cursor.fetchone()
        if result is None:
            print(f"⚠️  Warning: Destination {dest_id} not found, using default price")
            base_price = 100.0
        else:
            base_price = result[0]
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
        
        # VERIFY: Get package duration and price, ensure package exists
        cursor.execute('SELECT duration_days, price FROM packages WHERE id = ?', (package_id,))
        result = cursor.fetchone()
        if result is None:
            print(f"⚠️  Warning: Package {package_id} not found, skipping booking")
            continue
        duration, base_price = result
        
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
        # VERIFY: Get booking total price, ensure booking exists
        cursor.execute('SELECT total_price FROM bookings WHERE id = ?', (booking_id,))
        result = cursor.fetchone()
        if result is None:
            continue  # Skip if booking doesn't exist
        booking_price = result[0]
        
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
    
    # Insert cases
    print("Inserting support cases...")
    case_types = list(CASE_TYPES)
    case_statuses = list(CASE_STATUS)
    case_priorities = list(CASE_PRIORITY)
    agent_names = list(AGENT_NAMES)
    
    # Define which case types should link to bookings
    booking_related_types = [
        "Booking Issue", "Payment Issue", "Billing", "Cancellation Request", 
        "Refund Request", "Complaint"
    ]
    non_booking_types = [
        "Account Management", "Technical Support", "Travel Inquiry", 
        "Customer Support", "Product Feedback", "Other"
    ]
    
    num_cases = min(num_customers, 800)
    case_data = []
    
    for i in range(num_cases):
        # Decide if this case should link to a booking (70% of cases)
        should_link_booking = random.random() < 0.7 and num_bookings > 0
        
        # Choose case type based on whether we're linking to a booking
        if should_link_booking:
            case_type = random.choice(booking_related_types)
            booking_id = random.randint(1, num_bookings)
            
            # VERIFY: Get customer_id from the booking to ensure consistency
            cursor.execute('SELECT customer_id FROM bookings WHERE id = ?', (booking_id,))
            result = cursor.fetchone()
            if result is None:
                print(f"⚠️  Warning: Booking {booking_id} not found, skipping case")
                continue
            customer_id = result[0]
        else:
            case_type = random.choice(non_booking_types)
            booking_id = None
            customer_id = random.randint(1, num_customers)
        
        # Get matching subject and description for the case type
        subject = random.choice(CASE_SUBJECTS_BY_TYPE[case_type])
        description = random.choice(CASE_DESCRIPTIONS_BY_TYPE[case_type])
        status = random.choice(case_statuses)
        
        # Assign priority based on case type with realistic distribution
        # Critical cases should be rare (5%) and specific to urgent situations
        subject_lower = subject.lower()
        is_urgent = any(keyword in subject_lower for keyword in ["urgent", "emergency", "critical", "immediate"])
        
        if case_type in ["Cancellation Request", "Complaint"] and is_urgent:
            # Emergency-related cases have higher chance of being critical
            priority = random.choices(
                ["Low", "Medium", "High", "Critical"],
                weights=[5, 15, 40, 40]
            )[0]
        elif case_type in ["Complaint", "Refund Request", "Payment Issue"]:
            # Complaints, refunds, and payment issues tend to be higher priority
            priority = random.choices(
                ["Low", "Medium", "High", "Critical"],
                weights=[10, 30, 50, 10]
            )[0]
        elif case_type in ["Cancellation Request", "Booking Issue"]:
            # Cancellations and booking issues are moderately urgent
            priority = random.choices(
                ["Low", "Medium", "High", "Critical"],
                weights=[15, 35, 45, 5]
            )[0]
        elif case_type in ["Technical Support", "Account Management"]:
            # Tech and account issues are usually medium priority
            priority = random.choices(
                ["Low", "Medium", "High", "Critical"],
                weights=[20, 50, 28, 2]
            )[0]
        else:
            # General inquiries, feedback, etc. are usually low to medium priority
            priority = random.choices(
                ["Low", "Medium", "High", "Critical"],
                weights=[40, 45, 14, 1]
            )[0]
        
        # 80% of cases are assigned to an agent
        if random.random() < 0.8:
            assigned_to = random.choice(agent_names)
        else:
            assigned_to = None
        
        # Created date (within last 6 months)
        created_days_ago = random.randint(0, 180)
        created_at = datetime.now() - timedelta(days=created_days_ago)
        created_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Updated date (between created and now)
        updated_days_ago = random.randint(0, created_days_ago)
        updated_at = datetime.now() - timedelta(days=updated_days_ago)
        updated_str = updated_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Resolved date (only if status is Resolved or Closed)
        if status in ['Resolved', 'Closed']:
            resolved_days_ago = random.randint(0, updated_days_ago)
            resolved_at = datetime.now() - timedelta(days=resolved_days_ago)
            resolved_str = resolved_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            resolved_str = None
        
        case_data.append((
            customer_id, booking_id, case_type, subject, description,
            status, priority, assigned_to, created_str, updated_str, resolved_str
        ))
    
    cursor.executemany('''
        INSERT INTO cases (customer_id, booking_id, case_type, subject, description,
                          status, priority, assigned_to, created_at, updated_at, resolved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', case_data)
    
    conn.commit()
    
    # VERIFY: Run relationship checks before closing
    print("\n" + "="*60)
    print("🔍 Verifying Database Relationships...")
    print("="*60)
    
    verification_passed = True
    
    # Check 1: Packages -> Destinations
    cursor.execute('''
        SELECT COUNT(*) FROM packages 
        WHERE destination_id NOT IN (SELECT id FROM destinations)
    ''')
    orphan_packages = cursor.fetchone()[0]
    if orphan_packages > 0:
        print(f"❌ {orphan_packages} packages reference non-existent destinations")
        verification_passed = False
    else:
        print(f"✅ All {num_packages} packages have valid destination references")
    
    # Check 2: Bookings -> Customers and Packages
    cursor.execute('''
        SELECT COUNT(*) FROM bookings 
        WHERE customer_id NOT IN (SELECT id FROM customers)
        OR package_id NOT IN (SELECT id FROM packages)
    ''')
    orphan_bookings = cursor.fetchone()[0]
    if orphan_bookings > 0:
        print(f"❌ {orphan_bookings} bookings have invalid customer or package references")
        verification_passed = False
    else:
        cursor.execute('SELECT COUNT(*) FROM bookings')
        actual_bookings = cursor.fetchone()[0]
        print(f"✅ All {actual_bookings} bookings have valid customer and package references")
    
    # Check 3: Payments -> Bookings
    cursor.execute('''
        SELECT COUNT(*) FROM payments 
        WHERE booking_id NOT IN (SELECT id FROM bookings)
    ''')
    orphan_payments = cursor.fetchone()[0]
    if orphan_payments > 0:
        print(f"❌ {orphan_payments} payments reference non-existent bookings")
        verification_passed = False
    else:
        print(f"✅ All {len(payment_data)} payments have valid booking references")
    
    # Check 4: Cases -> Customers and Bookings
    cursor.execute('''
        SELECT COUNT(*) FROM cases 
        WHERE customer_id NOT IN (SELECT id FROM customers)
    ''')
    orphan_cases = cursor.fetchone()[0]
    if orphan_cases > 0:
        print(f"❌ {orphan_cases} cases reference non-existent customers")
        verification_passed = False
    else:
        print(f"✅ All {len(case_data)} cases have valid customer references")
    
    cursor.execute('''
        SELECT COUNT(*) FROM cases 
        WHERE booking_id IS NOT NULL 
        AND booking_id NOT IN (SELECT id FROM bookings)
    ''')
    orphan_case_bookings = cursor.fetchone()[0]
    if orphan_case_bookings > 0:
        print(f"❌ {orphan_case_bookings} cases reference non-existent bookings")
        verification_passed = False
    else:
        cursor.execute('SELECT COUNT(*) FROM cases WHERE booking_id IS NOT NULL')
        cases_with_bookings = cursor.fetchone()[0]
        print(f"✅ All {cases_with_bookings} booking-linked cases have valid references")
    
    # Check 5: Case-Booking-Customer consistency
    cursor.execute('''
        SELECT COUNT(*) FROM cases c
        INNER JOIN bookings b ON c.booking_id = b.id
        WHERE c.customer_id != b.customer_id
    ''')
    mismatched = cursor.fetchone()[0]
    if mismatched > 0:
        print(f"❌ {mismatched} cases have mismatched customer_id with their linked booking")
        verification_passed = False
    else:
        print(f"✅ All booking-linked cases match the booking's customer")
    
    # Get final statistics
    cursor.execute('SELECT COUNT(DISTINCT customer_id) FROM bookings')
    customers_with_bookings = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT customer_id) FROM cases')
    customers_with_cases = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM cases WHERE booking_id IS NULL')
    cases_without_bookings = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "="*60)
    if verification_passed:
        print("✅ ALL VERIFICATION CHECKS PASSED!")
    else:
        print("⚠️  SOME VERIFICATION CHECKS FAILED - Review above")
    print("="*60)
    
    print(f"\n✓ Database generated successfully at {path}!")
    print(f"\n📊 Summary Statistics:")
    print(f"  Tables:")
    print(f"    • {num_customers:,} customers")
    print(f"    • {num_destinations} destinations")
    print(f"    • {num_packages} packages")
    print(f"    • {len(booking_data):,} bookings")
    print(f"    • {len(payment_data):,} payments")
    print(f"    • {len(case_data):,} support cases")
    print(f"\n  Relationships:")
    print(f"    • {customers_with_bookings:,} customers have bookings ({customers_with_bookings/num_customers*100:.1f}%)")
    print(f"    • {customers_with_cases:,} customers have cases ({customers_with_cases/num_customers*100:.1f}%)")
    print(f"    • {cases_with_bookings:,} cases linked to bookings ({cases_with_bookings/len(case_data)*100:.1f}%)")
    print(f"    • {cases_without_bookings:,} cases without booking link ({cases_without_bookings/len(case_data)*100:.1f}%)")

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