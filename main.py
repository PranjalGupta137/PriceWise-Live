from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# Tables create karna
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CONFIGURATION ---
REFERRAL_CODE = "PRANJAL50"
MY_UPI_ID = "pranjal12345786@okaxis"

# Function to seed products if DB is empty
def seed_data(db: Session):
    if not db.query(models.Product).first():
        items = [
            ("Tomato", "kg"), ("Onion", "kg"), ("Potato", "kg"),
            ("Milk", "1L"), ("Paneer", "200g"), ("Bread", "Packet"),
            ("Atta", "5kg"), ("Oil", "1L"), ("Sugar", "kg")
        ]
        for name, unit in items:
            p = models.Product(name=name, base_unit=unit)
            db.add(p)
            db.commit()
            db.refresh(p)
            # Dummy prices for start (Scraper will update these later)
            h1 = models.PriceHistory(product_id=p.id, vendor="Local Mandi", price=40.0)
            h2 = models.PriceHistory(product_id=p.id, vendor="Blinkit/Zepto", price=60.0)
            db.add_all([h1, h2])
        db.commit()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    seed_data(db)
    query = request.query_params.get("search", "").capitalize()
    
    if query:
        products = db.query(models.Product).filter(models.Product.name.contains(query)).all()
    else:
        products = db.query(models.Product).all()

    table_rows = ""
    for prod in products:
        mandi = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Local Mandi").order_by(models.PriceHistory.timestamp.desc()).first()
        online = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Blinkit/Zepto").order_by(models.PriceHistory.timestamp.desc()).first()

        if mandi and online:
            buy_link = f"https://www.bigbasket.com/ps/?q={prod.name}&referral_code={REFERRAL_CODE}"
            table_rows += f"""
            <div class="card">
                <p class="title">{prod.name} ({prod.base_unit})</p>
                <div class="prices">
                    <span class="mandi">Mandi: ₹{mandi.price}</span>
                    <span class="online">Online: ₹{online.price}</span>
                </div>
                <a href="{buy_link}" target="_blank" class="btn">Compare & Buy</a>
            </div>"""

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: sans-serif; background: #f4f7f6; margin: 0; padding-bottom: 70px; }}
            .header {{ background: #318616; color: white; padding: 20px; text-align: center; position: sticky; top: 0; }}
            .search-box {{ padding: 15px; text-align: center; }}
            .search-box input {{ width: 80%; padding: 12px; border-radius: 25px; border: 1px solid #ddd; outline: none; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }}
            .card {{ background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .title {{ font-weight: bold; font-size: 15px; margin: 0; }}
            .prices {{ margin-top: 10px; font-size: 13px; }}
            .mandi {{ color: #2e7d32; font-weight: bold; display: block; }}
            .online {{ color: #999; text-decoration: line-through; }}
            .btn {{ display: block; background: #318616; color: white; text-align: center; padding: 8px; border-radius: 6px; text-decoration: none; margin-top: 10px; font-size: 12px; font-weight: bold; }}
            .footer {{ position: fixed; bottom: 0; width: 100%; background: #000; color: #fff; padding: 15px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header"><h2>PriceWise Store</h2></div>
        <div class="search-box">
            <form action="/"><input type="text" name="search" placeholder="Search vegetables, milk, atta..."></form>
        </div>
        <div class="grid">{table_rows if table_rows else "<p style='grid-column: 1/3;'>No products found.</p>"}</div>
        <div class="footer">🚀 BIGGER SAVINGS ON EVERY ITEM!</div>
    </body>
    </html>"""
