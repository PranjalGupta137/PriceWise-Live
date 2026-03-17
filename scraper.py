import requests
from bs4 import BeautifulSoup
from database import SessionLocal
from models import Product, PriceHistory
import time

def fetch_online_price(product_name):
    # BigBasket/Blinkit search URL (Example logic)
    search_url = f"https://www.bigbasket.com/ps/?q={product_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BigBasket ke HTML se price nikalne ka logic
        # Note: Actual class names change hoti rehti hain, hum ise update karte rahenge
        price_tag = soup.find("span", {"class": "discnt-price"}) 
        if price_tag:
            price_text = price_tag.text.replace("₹", "").strip()
            return float(price_text)
    except Exception as e:
        print(f"Error fetching {product_name}: {e}")
    
    return None

def update_all_prices():
    db = SessionLocal()
    products = db.query(Product).all()
    
    for prod in products:
        print(f"Updating {prod.name}...")
        real_price = fetch_online_price(prod.name)
        
        if real_price:
            new_price = PriceHistory(
                product_id=prod.id,
                vendor="Online (BB/Blinkit)",
                price=real_price
            )
            db.add(new_price)
            # Mandi price logic: Usually Mandi is 30-40% cheaper
            mandi_price = PriceHistory(
                product_id=prod.id,
                vendor="Local Mandi",
                price=round(real_price * 0.65, 2)
            )
            db.add(mandi_price)
            db.commit()
    db.close()

if __name__ == "__main__":
    while True:
        update_all_prices()
        print("Waiting 1 hour for next sync...")
        time.sleep(3600)
