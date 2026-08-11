# generate_data.py
import pandas as pd
import numpy as np
import random

# Set random seeds for reproducible synthetic data
np.random.seed(42)
random.seed(42)

TOTAL_RECORDS = 1000

# Base realistic vendor master names
base_vendors = [
    "Acme Solutions Inc", "Global Tech Logistics", "Apex Consulting Group", 
    "Nexus Data Systems", "Vanguard Industrial Corp", "Horizon Media Works",
    "Omni Global Trade", "Synergy Health Tech", "Summit Financial Partners",
    "Pinnacle Software Labs", "Meridian Supply Chain", "Beacon Analytics"
]

# Common variations to simulate real enterprise MDM noise
def corrupt_name(name):
    choice = random.random()
    if choice < 0.15:
        return name.lower()
    elif choice < 0.30:
        return name.replace("Inc", "Inc.").replace("Group", "Grp").replace("Corp", "Corporation")
    elif choice < 0.40:
        return name + " Ltd"
    elif choice < 0.45:
        return name[:4] # Truncated entry
    return name

regions = ["North America", "EMEA", "APAC", "LATAM"]
domains = ["com", "org", "io", "net"]

data = []

for i in range(1, TOTAL_RECORDS + 1):
    vendor_id = f"V-{1000 + i}"
    
    # Randomly select a base vendor template to simulate realistic duplicates
    base_name = random.choice(base_vendors)
    vendor_name = corrupt_name(base_name)
    
    # Email generation with deliberate quality issues
    if random.random() < 0.08:
        email = None  # Missing attribute
    elif random.random() < 0.05:
        email = "invalid_email_format"  # Data quality violation
    else:
        clean_prefix = base_name.split()[0].lower()
        domain = random.choice(domains)
        email = f"contact@{clean_prefix}.{domain}"
        
    # Tax ID generation with duplicates and missing values
    if random.random() < 0.07:
        tax_id = None
    else:
        base_tax_num = abs(hash(base_name)) % 89999 + 10000
        tax_id = f"TX-{base_tax_num}"

    # Invoice amounts for statistical distribution analysis
    invoice_amount = round(float(np.random.exponential(scale=25000) + 1200), 2)
    
    # Region assignment
    region = random.choice(regions) if random.random() > 0.03 else None
    
    data.append({
        "Vendor_ID": vendor_id,
        "Vendor_Name": vendor_name,
        "Contact_Email": email,
        "Tax_ID": tax_id,
        "Invoice_Amount": invoice_amount,
        "Region": region
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Inject explicit exact duplicates (5% of the dataset)
duplicate_rows = df.sample(frac=0.05, random_state=42)
df = pd.concat([df, duplicate_rows], ignore_index=True)

# Save generated dataset
df.to_csv("raw_vendor_data.csv", index=False)
print(f"Dataset generation complete: raw_vendor_data.csv created with {len(df)} total records.")