import time
import random
from database import SessionLocal
from models import Product, PriceHistory

def run_real_time_sync():
    db = SessionLocal()
    # Jin products ka data chahiye
    products_to_sync = ["Tomato", "Onion", "Potato", "Ginger", "Lemon"]
    
    print("🔄 Syncing Real-time Prices...")
    
    for name in products_to_sync:
        # DB mein product entry check karna
        product = db.query(Product).filter_by(name=name).first()
        if not product:
            product = Product(name=name, base_unit="kg")
            db.add(product)
            db.commit()
            db.refresh(product)

        # REAL LOGIC: Yahan hum real mandi rates ko simulate kar rahe hain
        # In Production: Yahan requests.get() aayega Govt API ke liye
        base_mandi_price = random.uniform(20, 60) 
        online_markup = random.uniform(1.2, 1.5) # Online 20-50% mehnga hota hai

        # 1. Update Mandi Price
        mandi_entry = PriceHistory(
            product_id=product.id,
            vendor="Local Mandi (Sangam Vihar)",
            price=round(base_mandi_price, 2)
        )
        
        # 2. Update Online Price (Blinkit/Zepto Proxy)
        online_entry = PriceHistory(
            product_id=product.id,
            vendor="Blinkit/Zepto",
            price=round(base_mandi_price * online_markup, 2)
        )

        db.add(mandi_entry)
        db.add(online_entry)
        print(f"✅ Updated {name}: Mandi ₹{round(base_mandi_price,1)} | Online ₹{round(base_mandi_price*online_markup,1)}")

    db.commit()
    db.close()
    print("🚀 All Prices Synced!")

if __name__ == "__main__":
    while True:
        run_real_time_sync()
        print("Sleeping for 1 hour...")
        time.sleep(3600) # Har 1 ghante mein auto-run