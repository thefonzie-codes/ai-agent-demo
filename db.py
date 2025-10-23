import sqlite3
import random

def generate_db():
    first_names = [
      "Ethan", "Olivia", "Liam", "Emma", "Noah", "Ava", "William",
      "Sophia", "James", "Isabella", "Benjamin", "Charlotte", "Lucas",
      "Amelia", "Henry", "Mia", "Alexander", "Evelyn", "Theodore", "Harper"
    ]

    last_names = [
      "Ramirez", "Sterling", "Chen", "O'Connell", "Patel", "Sinclair",
      "Johnson", "Schwartz", "Garcia", "Kim", "Rodriguez", "Dubois",
      "Wilson", "Green", "Baker", "Novak", "Carter", "Lopez", "Singh", "Chang"
    ]

    phone_numbers = [
      "(555) 555-6019", "(555) 555-4721", "(555) 555-3850", "(555) 555-9143",
      "(555) 555-0628", "(555) 555-7354", "(555) 555-2907", "(555) 555-8462",
      "(555) 555-1539", "(555) 555-6274", "(555) 555-0985", "(555) 555-3160",
      "(555) 555-7492", "(555) 555-5026", "(555) 555-4381", "(555) 555-2713",
      "(555) 555-9658", "(555) 555-1847", "(555) 555-0376", "(555) 555-6904",
      "(555) 555-8251", "(555) 555-4039", "(555) 555-7561", "(555) 555-2198",
      "(555) 555-9345", "(555) 555-0812", "(555) 555-3670", "(555) 555-5423",
      "(555) 555-1709", "(555) 555-6538", "(555) 555-4987", "(555) 555-0215",
      "(555) 555-3746", "(555) 555-9052", "(555) 555-7831", "(555) 555-1640",
      "(555) 555-5293", "(555) 555-8174", "(555) 555-2469", "(555) 555-6305",
      "(555) 555-4518", "(555) 555-0723", "(555) 555-3961", "(555) 555-7184",
      "(555) 555-5806", "(555) 555-2097", "(555) 555-8634", "(555) 555-1325",
      "(555) 555-9470", "(555) 555-6853", "(555) 555-4209", "(555) 555-7638",
      "(555) 555-3017", "(555) 555-5942", "(555) 555-1086", "(555) 555-8354",
      "(555) 555-2579", "(555) 555-6701", "(555) 555-0493", "(555) 555-4825",
      "(555) 555-7910", "(555) 555-3268", "(555) 555-5647", "(555) 555-1129",
      "(555) 555-9703", "(555) 555-6450", "(555) 555-0581", "(555) 555-8832",
      "(555) 555-2346", "(555) 555-4197", "(555) 555-7065", "(555) 555-3394",
      "(555) 555-5712", "(555) 555-1980", "(555) 555-9256", "(555) 555-6147",
      "(555) 555-0038", "(555) 555-8570", "(555) 555-2813", "(555) 555-4609",
      "(555) 555-7724", "(555) 555-3451", "(555) 555-5389", "(555) 555-1206",
      "(555) 555-9837", "(555) 555-6695", "(555) 555-0172", "(555) 555-8743",
      "(555) 555-2258", "(555) 555-4460", "(555) 555-7281", "(555) 555-3509",
      "(555) 555-5136", "(555) 555-1492", "(555) 555-9964", "(555) 555-6028",
      "(555) 555-0315", "(555) 555-8497", "(555) 555-2630", "(555) 555-4903"
    ]

    customer_support_tags = [
        "Billing / Payment",
        "Technical / Bug",
        "Account / Login",
        "Feature Request / Feedback",
        "Shipping / Delivery"
    ]

    mock_customer_data = []
    for i in range(100):
      first = random.choice(first_names)
      last = random.choice(last_names)
      issue = random.choice(customer_support_tags)
      email_address = f"{first}{last}@example.com" 

      mock_customer_data.append((
        first,
        last,
        email_address,
        phone_numbers[i],
        issue
      ))

    conn = sqlite3.connect('customer_db.db')
    # database operations here
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            issue TEXT NOT NULL
        )
      '''
    )
    
    cursor.executemany("INSERT INTO customers (first_name, last_name, email, phone, issue) VALUES (?, ?, ?, ?, ?)", mock_customer_data)
    conn.commit()
    conn.close()