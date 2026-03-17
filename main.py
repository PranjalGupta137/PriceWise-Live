from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# Tables automatically create karna
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PriceWise AI - Mega Blinkit Clone")

# --- CONFIGURATION ---
REFERRAL_CODE = "PRANJAL50"
MY_UPI_ID = "pranjal12345786@okaxis"

# Badi Inventory ka Base (Ye sirf shuruat hai, search se aur badhenge)
def get_universal_inventory():
    return {
        "Vegetables": [("Tomato", "1 kg", 40, 65, "tomato"), ("Onion", "1 kg", 30, 55, "onion"), ("Potato", "1 kg", 25, 45, "potato"), ("Ginger", "100 g", 15, 25, "ginger"), ("Garlic", "100 g", 20, 40, "garlic")],
        "Fruits": [("Apple", "1 kg", 120, 180, "apple"), ("Banana", "6 pcs", 30, 55, "banana"), ("Papaya", "1 pc", 40, 70, "papaya"), ("Grapes", "500 g", 50, 90, "grapes")],
        "Dairy & Eggs": [("Amul Milk", "500 ml", 32, 34, "milk"), ("Paneer", "200 g", 85, 115, "cheese"), ("Eggs", "6 pcs", 45, 65, "egg"), ("Curd", "400 g", 35, 50, "yogurt")],
        "Grocery": [("Atta", "5 kg", 190, 250, "flour"), ("Sugar", "1 kg", 42, 55, "sugar"), ("Dal Tadka", "1 kg", 90, 140, "lentils"), ("Rice", "1 kg", 55, 90, "rice")],
        "Snacks": [("Maggi", "70 g", 12, 14, "noodles"), ("Chips", "Packet", 10, 20, "chips"), ("Biscuits", "Packet", 20, 35, "biscuit")]
    }

def seed_mega_inventory(db: Session):
    if not db.query(models.Product).first():
        inventory = get_universal_inventory()
        for cat, items in inventory.items():
            for name, unit, m_price, o_price, img_tag in items:
                p = models.Product(name=name, base_unit=unit)
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
    seed_mega_inventory(db)
    query = request.query_params.get("search", "").capitalize()
    
    # Search Filter
    products_query = db.query(models.Product)
    if query:
        products = products_query.filter(models.Product.name.contains(query)).all()
    else:
        products = products_query.all()
    
    product_cards = ""
    for prod in products:
        mandi = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Local Mandi").order_by(models.PriceHistory.timestamp.desc()).first()
        online = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Blinkit/Zepto").order_by(models.PriceHistory.timestamp.desc()).first()

        if mandi and online:
            savings = int(online.price - mandi.price)
            # Fix: Reliable image source
            img_url = f"https://img.icons8.com/fluency/96/{prod.name.split()[0].lower()}.png"
            buy_link = f"https://www.bigbasket.com/ps/?q={prod.name}&referral_code={REFERRAL_CODE}"
            
            product_cards += f"""
            <div class="p-card">
                <div class="save-tag">Bachat ₹{savings}</div>
                <img src="{img_url}" class="p-img" onerror="this.src='https://img.icons8.com/fluency/96/box.png'">
                <p class="p-name">{prod.name}</p>
                <p class="p-unit">{prod.base_unit}</p>
                <div class="p-prices">
                    <div class="price-box">
                        <span class="m-price">₹{mandi.price}</span>
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
            :root {{ --blinkit-yellow: #f7d54e; --green: #1c890e; --light-bg: #f8f9fb; }}
            body {{ font-family: 'Inter', sans-serif; background: var(--light-bg); margin: 0; padding-bottom: 90px; }}
            .header {{ background: var(--blinkit-yellow); padding: 15px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .search-bar {{ background: #fff; padding: 12px 15px; border-radius: 12px; display: flex; align-items: center; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }}
            .search-bar input {{ border: none; outline: none; width: 100%; font-size: 16px; font-weight: 500; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 12px; }}
            .p-card {{ background: #fff; border-radius: 16px; padding: 12px; border: 1px solid #f0f0f0; display: flex; flex-direction: column; position: relative; transition: 0.2s; }}
            .save-tag {{ position: absolute; top: 0; left: 0; background: var(--green); color: #fff; font-size: 10px; padding: 3px 8px; border-radius: 16px 0 16px 0; font-weight: 900; }}
            .p-img {{ width: 70px; height: 70px; align-self: center; margin: 15px 0; object-fit: contain; }}
            .p-name {{ font-weight: 700; font-size: 14px; margin: 0; color: #1a1a1a; min-height: 34px; }}
            .p-unit {{ color: #777; font-size: 11px; margin-bottom: 8px; }}
            .p-prices {{ display: flex; justify-content: space-between; align-items: flex-end; }}
            .price-box {{ display: flex; flex-direction: column; }}
            .m-price {{ font-size: 17px; font-weight: 900; color: #000; }}
            .o-price {{ font-size: 11px; color: #999; text-decoration: line-through; }}
            .add-btn {{ background: #fff; color: var(--green); border: 1px solid var(--green); padding: 6px 20px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 12px; }}
            .footer-nav {{ position: fixed; bottom: 0; width: 100%; background: #fff; padding: 12px 0; border-top: 1px solid #eee; display: flex; justify-content: space-around; }}
        </style>
    </head>
    <body>
        <div class="header">
            <form action="/" class="search-bar">
                <input type="text" name="search" placeholder="Search from 10,000+ items...">
            </form>
        </div>
        <div class="grid">{product_cards if product_cards else "<p style='grid-column: 1/3; text-align:center;'>Blinkit par ye item abhi available nahi hai!</p>"}</div>
        <div class="footer-nav">
            <a href="/" style="text-decoration:none; color:var(--green); font-weight:bold;">🏠 Home</a>
            <a href="/premium" style="text-decoration:none; color:#666; font-weight:bold;">💎 Premium</a>
        </div>
    </body>
    </html>
    """

@app.get("/premium", response_class=HTMLResponse)
def premium():
    qr_data = f"upi://pay?pa={MY_UPI_ID}&pn=PranjalGupta&am=49"
    return f"""<body style="text-align:center; padding:40px; font-family:sans-serif; background:#f4f4f4;">
        <div style="background:#fff; padding:30px; border-radius:24px; box-shadow:0 10px 25px rgba(0,0,0,0.1); display:inline-block;">
            <h2 style="color:#1c890e;">🚀 PriceWise Premium</h2>
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}" style="border:5px solid #1c890e; border-radius:12px; margin:20px 0;">
            <p style="font-weight:bold;">Pay ₹49 for Daily Mandi Alerts on WhatsApp</p>
            <a href="https://wa.me/91XXXXXXXXXX" style="background:#25D366; color:#fff; padding:15px 30px; text-decoration:none; border-radius:12px; font-weight:bold; display:block;">I've Paid - Message Pranjal</a>
        </div>
    </body>"""
