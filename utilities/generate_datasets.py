#!/usr/bin/env python3
"""
Simple synthetic data generator for testing the claims pipeline.
Produces CSVs for claims, members, and providers.
"""

import csv
import os
import random
import uuid
from datetime import date, timedelta

# Just a bunch of lookup codes to keep it realistic-ish
ICD10 = ["I10", "E11.9", "J06.9", "M54.5", "Z00.00", "F32.9", "K21.0"]
CPT = ["99213", "99214", "99232", "99283", "99385", "71046"]
STATES = ["CA", "TX", "FL", "NY", "IL", "PA"]
STATUS = ["APPROVED", "APPROVED", "REJECTED", "PENDING"]

def get_random_date(start_year=2023):
    start = date(start_year, 1, 1)
    end = date.today()
    return start + timedelta(days=random.randint(0, (end - start).days))

def generate_data(rows=1000):
    print(f"Generating {rows} claim records...")
    
    # 1. Members
    members = []
    for i in range(100):
        members.append({
            "member_id": f"MBR{i:05d}",
            "member_name": f"Member_{i}",
            "state": random.choice(STATES),
            "insurance_plan_id": f"PLAN-{random.randint(1,5)}"
        })
    
    # 2. Providers
    providers = []
    for i in range(20):
        providers.append({
            "provider_id": f"PRV{i:03d}",
            "provider_name": f"Provider_{i}",
            "state": random.choice(STATES),
            "network_status": random.choice(["IN_NETWORK", "OUT_OF_NETWORK"])
        })
        
    # 3. Claims
    claims = []
    for _ in range(rows):
        dt = get_random_date()
        amt = round(random.uniform(50.0, 5000.0), 2)
        # Small chance of a "bad" record for the quarantine test
        bad_rec = random.random() < 0.02
        
        claims.append({
            "claim_id": "" if bad_rec else f"CLM-{uuid.uuid4().hex[:8].upper()}",
            "member_id": random.choice(members)["member_id"],
            "provider_id": random.choice(providers)["provider_id"],
            "claim_date": dt.isoformat(),
            "claim_amount": -10.0 if bad_rec else amt,
            "claim_status": random.choice(STATUS)
        })
        
    return members, providers, claims

def save_csv(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved: {filename}")

if __name__ == "__main__":
    m, p, c = generate_data(5000)
    save_csv(m, "datasets/raw/members/members_init.csv")
    save_csv(p, "datasets/raw/providers/providers_init.csv")
    save_csv(c, f"datasets/raw/claims/claims_{date.today().isoformat()}.csv")
    print("Done.")
