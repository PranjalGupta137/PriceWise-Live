from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CONFIGURATION ---
REFERRAL_CODE = "PRANJAL50"

# Multi-Vendor Inventory Data
def seed_comparison_data(db: Session):
    if not db.query(models.Product).first():
        data = [
            # Name, Unit, Blinkit, Zepto, BigBasket, Image
            ("Tomato", "1 kg", 68, 72, 62, "https://cdn.grofers.com/app/images/products/sliding_image/1202a.jpg"),
            ("Onion", "1 kg", 58, 60, 55, "https://cdn.grofers.com/app/images/products/sliding_image/1203a.jpg"),
            ("Potato", "1 kg", 48, 45, 42, "https://cdn.grofers.com/app/images/products/sliding_image/1204a.jpg"),
            ("Amul Gold Milk", "500 ml", 34, 34, 33, "https://cdn.grofers.com/app/images/products/sliding_image/160a.jpg"),
            ("Maggi Masala", "70 g", 14, 14, 13, "https://cdn.grofers.com/app/images/products/sliding_image/105a.jpg"),
            ("Harvest Bread", "400 g", 50, 48, 45, "https://cdn.grofers.com/app/images/products/sliding_image/133a.jpg"),
            ("Coca-Cola", "750 ml", 45, 45, 40, "https://cdn.grofers.com/app/images/products/sliding_image/132a.jpg"),
            ("Lay's Classic", "50 g", 20, 20, 18, "https://cdn.grofers.com/app/images/products/sliding_image/301a.jpg")
        ]
        for name, unit, b_p, z_p, bb_p, img in data:
            p = models.Product(name=name, base_unit=unit)
            db.add(p)
            db.commit()
            db.refresh(p)
            db.add_all([
                models.PriceHistory(product_id=p.id, vendor="Blinkit", price=b_p),
                models.PriceHistory(product_id=p.id, vendor="Zepto", price=z_p),
                models.PriceHistory(product_id=p.id, vendor="BigBasket", price=bb_p)
            ])
        db.commit()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    seed_comparison_data(db)
    query = request.query_params.get("search", "").capitalize()
    products = db.query(models.Product).filter(models.Product.name.contains(query)).all() if query else db.query(models.Product).all()

    cards = ""
    for p in products:
        # Fetching latest prices for all vendors
        blinkit = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == p.id, models.PriceHistory.vendor == "Blinkit").order_by(models.PriceHistory.timestamp.desc()).first()
        zepto = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == p.id, models.PriceHistory.vendor == "Zepto").order_by(models.PriceHistory.timestamp.desc()).first()
        bb = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == p.id, models.PriceHistory.vendor == "BigBasket").order_by(models.PriceHistory.timestamp.desc()).first()
        
        prices = {"Blinkit": blinkit.price, "Zepto": zepto.price, "BigBasket": bb.price}
        cheapest_vendor = min(prices, key=prices.get)
        cheapest_price = prices[cheapest_vendor]
        
        # Real-time Image (Placeholder logic)
        img_url = f"https://cdn.grofers.com/app/images/products/sliding_image/1202a.jpg" # Default
        if "Onion" in p.name: img_url = "https://cdn.grofers.com/app/images/products/sliding_image/1203a.jpg"
        elif "Potato" in p.name: img_url = "https://cdn.grofers.com/app/images/products/sliding_image/1204a.jpg"
        elif "Milk" in p.name: img_url = "https://cdn.grofers.com/app/images/products/sliding_image/160a.jpg"
        elif "Bread" in p.name: img_url = "https://cdn.grofers.com/app/images/products/sliding_image/133a.jpg"

        cards += f"""
        <div class="comp-card">
            <div class="best-deal">Cheapest on {cheapest_vendor}</div>
            <div class="card-main">
                <img src="{img_url}">
                <div class="details">
                    <p class="p-name">{p.name}</p>
                    <p class="p-unit">{p.base_unit}</p>
                    <div class="price-grid">
                        <div class="price-item {'highlight' if cheapest_vendor == 'Blinkit' else ''}">
                            <span>Blinkit</span><b>₹{blinkit.price}</b>
                        </div>
                        <div class="price-item {'highlight' if cheapest_vendor == 'Zepto' else ''}">
                            <span>Zepto</span><b>₹{zepto.price}</b>
                        </div>
                        <div class="price-item {'highlight' if cheapest_vendor == 'BigBasket' else ''}">
                            <span>BigBasket</span><b>₹{bb.price}</b>
                        </div>
                    </div>
                    <a href="https://www.bigbasket.com/ps/?q={p.name}" class="go-btn">Buy @ ₹{cheapest_price}</a>
                </div>
            </div>
        </div>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{ --green: #0c831f; --bg: #f5f6f7; }}
            body {{ font-family: 'Inter', sans-serif; background: var(--bg); margin: 0; }}
            .header {{ background: #fff; padding: 15px; border-bottom: 1px solid #ddd; position: sticky; top:0; z-index:100; }}
            .search-bar {{ background: #f0f1f2; padding: 12px; border-radius: 10px; border: 1px solid #e0e0e0; }}
            .search-bar input {{ border:none; background:transparent; width:100%; outline:none; font-size:15px; }}
            .container {{ padding: 10px; display: flex; flex-direction: column; gap: 15px; }}
            .comp-card {{ background: #fff; border-radius: 15px; overflow: hidden; border: 1px solid #eee; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }}
            .best-deal {{ background: #fff3cd; color: #856404; font-size: 11px; padding: 5px 15px; font-weight: bold; border-bottom: 1px dotted #ffeeba; }}
            .card-main {{ display: flex; padding: 12px; gap: 15px; }}
            .card-main img {{ width: 90px; height: 90px; object-fit: contain; }}
            .details {{ flex: 1; }}
            .p-name {{ font-weight: bold; font-size: 16px; margin: 0; }}
            .p-unit {{ color: #777; font-size: 12px; margin-bottom: 10px; }}
            .price-grid {{ display: flex; justify-content: space-between; margin-bottom: 12px; background: #fafafa; padding: 8px; border-radius: 8px; }}
            .price-item {{ display: flex; flex-direction: column; align-items: center; font-size: 11px; flex: 1; }}
            .price-item b {{ font-size: 14px; color: #333; }}
            .highlight {{ color: var(--green) !important; }}
            .highlight b {{ color: var(--green) !important; border-bottom: 2px solid var(--green); }}
            .go-btn {{ display: block; background: var(--green); color: #fff; text-align: center; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div style="font-weight:900; color:var(--green); margin-bottom:10px;">PriceWise Comparison AI</div>
            <form action="/" class="search-bar"><input type="text" name="search" placeholder="Compare prices for Bread, Milk..."></form>
        </div>
        <div class="container">{cards}</div>
    </body>
    </html>
    """
