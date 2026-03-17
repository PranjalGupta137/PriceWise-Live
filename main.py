from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# Database tables create karna
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PriceWise AI - Blinkit Clone")

# --- CONFIGURATION ---
REFERRAL_CODE = "PRANJAL50"
MY_UPI_ID = "pranjal12345786@okaxis"

# Function: Database mein saara maal (products) bharna
def seed_all_products(db: Session):
    if not db.query(models.Product).first():
        # Category-wise products
        inventory = [
            ("Tomato", "kg", "Vegetables", 40, 65),
            ("Onion", "kg", "Vegetables", 30, 55),
            ("Potato", "kg", "Vegetables", 25, 45),
            ("Apple", "kg", "Fruits", 120, 180),
            ("Banana", "Dozen", "Fruits", 40, 70),
            ("Amul Milk", "1L", "Dairy", 64, 68),
            ("Paneer", "200g", "Dairy", 80, 110),
            ("Atta", "5kg", "Grocery", 180, 240),
            ("Sugar", "kg", "Grocery", 42, 52)
        ]
        for name, unit, cat, m_price, o_price in inventory:
            p = models.Product(name=name, base_unit=unit) # Note: models mein category field hai toh update karein
            db.add(p)
            db.commit()
            db.refresh(p)
            db.add_all([
                models.PriceHistory(product_id=p.id, vendor="Local Mandi", price=m_price),
                models.PriceHistory(product_id=p.id, vendor="Blinkit/Zepto", price=o_price)
            ])
        db.commit()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    seed_all_products(db)
    query = request.query_params.get("search", "").capitalize()
    cat_filter = request.query_params.get("cat", "")

    # Search aur Category logic
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
            buy_link = f"https://www.bigbasket.com/ps/?q={prod.name}&referral_code={REFERRAL_CODE}"
            product_cards += f"""
            <div class="p-card">
                <div class="save-tag">Save ₹{savings}</div>
                <p class="p-name">{prod.name}</p>
                <p class="p-unit">{prod.base_unit}</p>
                <div class="p-prices">
                    <span class="m-price">₹{mandi.price}</span>
                    <span class="o-price">₹{online.price}</span>
                </div>
                <a href="{buy_link}" target="_blank" class="add-btn">Compare & Buy</a>
            </div>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{ --green: #318616; --yellow: #f7d54e; --light: #f3f4f6; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--light); margin: 0; padding-bottom: 80px; }}
            .header {{ background: var(--yellow); padding: 15px; position: sticky; top: 0; z-index: 100; }}
            .search-bar {{ background: #fff; display: flex; padding: 10px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .search-bar input {{ border: none; outline: none; width: 100%; font-size: 16px; }}
            .cat-scroll {{ display: flex; overflow-x: auto; padding: 15px; gap: 10px; background: #fff; }}
            .cat-item {{ background: #fff; border: 1px solid #ddd; padding: 8px 15px; border-radius: 20px; white-space: nowrap; font-size: 13px; text-decoration:none; color:#000; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 12px; }}
            .p-card {{ background: #fff; border-radius: 15px; padding: 12px; position: relative; border: 1px solid #eee; }}
            .save-tag {{ position: absolute; top: 0; left: 0; background: var(--green); color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 15px 0 15px 0; font-weight: bold; }}
            .p-name {{ font-weight: bold; margin: 15px 0 2px 0; font-size: 15px; }}
            .p-unit {{ color: #888; font-size: 12px; margin-bottom: 10px; }}
            .p-prices {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
            .m-price {{ color: #000; font-weight: bold; font-size: 18px; }}
            .o-price {{ color: #999; text-decoration: line-through; font-size: 12px; }}
            .add-btn {{ display: block; border: 1px solid var(--green); color: var(--green); text-align: center; padding: 6px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px; }}
            .footer {{ position: fixed; bottom: 0; width: 100%; background: #fff; border-top: 1px solid #ddd; display: flex; justify-content: space-around; padding: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="search-bar">
                <form action="/" style="width:100%"><input type="text" name="search" placeholder="Search 'Paneer' or 'Tomato'"></form>
            </div>
        </div>
        <div class="cat-scroll">
            <a href="/" class="cat-item">All Items</a>
            <a href="/?search=Vegetable" class="cat-item">Vegetables</a>
            <a href="/?search=Fruit" class="cat-item">Fruits</a>
            <a href="/?search=Milk" class="cat-item">Dairy</a>
            <a href="/?search=Atta" class="cat-item">Grocery</a>
        </div>
        <div class="grid">{product_cards if product_cards else "<p>Mandi mein aaj ye nahi mila!</p>"}</div>
        <div class="footer">
            <a href="/" style="text-decoration:none; color:var(--green);">🏠 Home</a>
            <a href="/premium" style="text-decoration:none; color:#666;">💎 Premium</a>
        </div>
    </body>
    </html>
    """

@app.get("/premium", response_class=HTMLResponse)
def premium():
    # UPI QR Code logic (same as before)
    qr_data = f"upi://pay?pa={MY_UPI_ID}&pn=PranjalGupta&am=49"
    return f"""<body style="text-align:center; padding:50px; font-family:sans-serif;">
        <h2 style="color:#318616;">Unlock Daily Mandi Alerts</h2>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}">
        <p>Pay ₹49 to get Mandi rates on WhatsApp daily!</p>
        <a href="https://wa.me/91XXXXXXXXXX" style="background:#25D366; color:#fff; padding:10px 20px; text-decoration:none; border-radius:10px;">Contact Pranjal</a>
    </body>"""
