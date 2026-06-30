import csv
import random
from datetime import datetime, timedelta

output_file = "trades_500mb.csv"

# Generate 100 synthetic symbols like SYM001, SYM002, ..., SYM100
symbols = [f"SYM{str(i).zfill(3)}" for i in range(1, 101)]

start_time = datetime(2026, 4, 1, 10, 0, 0)

target_size_bytes = 100 * 1024 * 1024  # 500 MB
current_size = 0
trade_id = 1

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    
    # Write header
    writer.writerow(["trade_id", "symbol", "price", "quantity", "timestamp"])
    
    while current_size < target_size_bytes:
        symbol = random.choice(symbols)
        price = round(random.uniform(10, 1000), 2)
        quantity = random.randint(1, 5000)
        timestamp = start_time + timedelta(seconds=trade_id)
        
        writer.writerow([trade_id, symbol, price, quantity, timestamp.isoformat() + "Z"])
        
        trade_id += 1
        
        # Check file size periodically for performance
        if trade_id % 5000 == 0:
            current_size = f.tell()

print("Done! File generated:", output_file)