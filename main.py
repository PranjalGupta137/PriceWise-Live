from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# Database tables automatically create karna
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PriceWise AI - Ultimate Blinkit Clone")

# --- CONFIGURATION ---
REFERRAL_CODE = "PRANJAL50"
MY_UPI_ID = "pranjal12345786@okaxis"

# Sabse Badi Inventory (Hazaron items ke liye base)
def seed_all_products(db: Session):
    if not db.query(models.Product).first():
        inventory = [
            # Name, Unit, Mandi Price, Online Price, Image URL
            ("Tomato", "1 kg", 40, 65, "https://cdn-icons-png.flaticon.com/512/1202/1202125.png"),
            ("Onion", "1 kg", 30, 55, "https://cdn-icons-png.flaticon.com/512/7230/7230868.png"),
            ("Potato", "1 kg", 25, 45, "https://cdn-icons-png.flaticon.com/512/1135/1135543.png"),
            ("Apple", "1 kg", 120, 180, "https://cdn-icons-png.flaticon.com/512/415/415733.png"),
            ("Amul Milk", "500 ml", 32, 34, "https://cdn-icons-png.flaticon.com/512/2674/2674486.png"),
            ("Paneer", "200 g", 85, 110, "https://cdn-icons-png.flaticon.com/512/2321/2321588.png"),
            ("Atta", "5 kg", 190, 245, "https://cdn-icons-png.flaticon.com/512/2271/2271404.png"),
            ("Sugar", "1 kg", 42, 52, "https://cdn-icons-png.flaticon.com/512/5029/5029241.png"),
            ("Bread", "1 pkt", 35, 50, "https://cdn-icons-png.flaticon.com/512/992/992744.png"),
            ("Eggs", "6 pcs", 45, 60, "https://cdn-icons-png.flaticon.com/512/2713/2713474.png"),
            ("Banana", "6 pcs", 30, 50, "https://cdn-icons-png.flaticon.com/512/2909/2909761.png"),
            ("Ginger", "100 g", 15, 25, "https://cdn-icons-png.flaticon.com/512/3595/3595447.png")
        ]
        for name, unit, m_price, o_price, img in inventory:
            p = models.Product(name=name, base_unit=unit)
            db.add(p)
            db.commit()
            db.refresh(p)
            # Store image URL in a temporary way or custom logic
            db.add_all([
                models.PriceHistory(product_id=p.id, vendor="Local Mandi", price=m_price),
                models.PriceHistory(product_id=p.id, vendor="Blinkit/Zepto", price=o_price)
            ])
        db.commit()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    seed_all_products(db)
    query = request.query_params.get("search", "").capitalize()
    
    products_query = db.query(models.Product)
    if query:
        products_query = products_query.filter(models.Product.name.contains(query))
    
    products = products_query.all()
    product_cards = ""

    for prod in products:
        mandi = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Local Mandi").order_by(models.PriceHistory.timestamp.desc()).first()
        online = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Blinkit/Zepto").order_by(models.PriceHistory.timestamp.desc()).first()

        if mandi and online:
            savings = int(online.price - mandi.price)
            # Placeholder images logic based on name
            img_map = {
                "Tomato": "1202125", "Onion": "7230868", "Potato": "1135543", 
                "Apple": "415733", "Milk": "2674486", "Paneer": "2321588",
                "Atta": "2271404", "Sugar": "5029241", "Bread": "992744",
                "Eggs": "2713474", "Banana": "2909761", "Ginger": "3595447"
            }
            icon_id = "2321588" # Default icon
            for key in img_map:
                if key in prod.name: icon_id = img_map[key]
            
            img_url = f"https://cdn-icons-png.flaticon.com/512/{icon_id[0:4]}/{icon_id}.png"
            buy_link = f"https://www.bigbasket.com/ps/?q={prod.name}&referral_code={REFERRAL_CODE}"
            
            product_cards += f"""
            <div class="p-card">
                <div class="save-tag">SAVE ₹{savings}</div>
                <img src="{img_url}" class="p-img">
                <p class="p-name">{prod.name}</p>
                <p class="p-unit">{prod.base_unit}</p>
                <div class="p-prices">
                    <div>
                        <span class="m-price">₹{mandi.price}</span><br>
                        <span class="o-price">₹{online.price}</span>
                    </div>
                    <a href="{buy_link}" target="_blank" class="add-btn">ADD</a>
                </div>
            </div>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{ --primary: #318616; --accent: #f7d54e; --bg: #f8f9fb; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding-bottom: 80px; }}
            .header {{ background: var(--accent); padding: 15px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .search-bar {{ background: #fff; padding: 10px 15px; border-radius: 12px; display: flex; align-items: center; }}
            .search-bar input {{ border: none; outline: none; width: 100%; font-size: 15px; font-weight: 500; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 15px; }}
            .p-card {{ background: #fff; border-radius: 18px; padding: 12px; border: 1px solid #f0f0f0; position: relative; display: flex; flex-direction: column; justify-content: space-between; }}
            .save-tag {{ position: absolute; top: 0; left: 0; background: var(--primary); color: #fff; font-size: 10px; padding: 3px 8px; border-radius: 18px 0 18px 0; font-weight: bold; }}
            .p-img {{ width: 80px; height: 80px; align-self: center; object-fit: contain; margin: 10px 0; }}
            .p-name {{ font-weight: 700; font-size: 14px; margin: 0; color: #1f1f1f; }}
            .p-unit {{ color: #777; font-size: 11px; margin: 2px 0 10px 0; }}
            .p-prices {{ display: flex; justify-content: space-between; align-items: center; }}
            .m-price {{ font-size: 16px; font-weight: 800; color: #000; }}
            .o-price {{ font-size: 11px; color: #999; text-decoration: line-through; }}
            .add-btn {{ border: 1px solid var(--primary); color: var(--primary); padding: 5px 18px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 12px; }}
            .footer {{ position: fixed; bottom: 0; width: 100%; background: #fff; padding: 12px; display: flex; justify-content: space-around; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="header">
            <form action="/" class="search-bar">
                <input type="text" name="search" placeholder="Search vegetables, dairy, snacks...">
            </form>
        </div>
        <div class="grid">{product_cards if product_cards else "<p>No results found</p>"}</div>
        <div class="footer">
            <a href="/" style="text-decoration:none; color:var(--primary); font-weight:bold;">🏠 Home</a>
            <a href="/premium" style="text-decoration:none; color:#666; font-weight:bold;">💎 Premium</a>
        </div>
    </body>
    </html>
    """

@app.get("/premium", response_class=HTMLResponse)
def premium():
    qr_data = f"upi://pay?pa={MY_UPI_ID}&pn=PranjalGupta&am=49"
    return f"""<body style="text-align:center; padding:40px; font-family:sans-serif; background:#f4f4f4;">
        <div style="background:#fff; padding:30px; border-radius:20px; display:inline-block;">
            <h2 style="color:#318616;">Unlock Premium Alerts</h2>
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}" style="border:4px solid #318616; border-radius:10px;">
            <p>Pay ₹49 to get Daily Mandi Rates on WhatsApp</p>
            <a href="https://wa.me/91XXXXXXXXXX" style="background:#25D366; color:#fff; padding:12px 24px; text-decoration:none; border-radius:10px; font-weight:bold; display:block; margin-top:15px;">Message Pranjal</a>
        </div>
    </body>"""
