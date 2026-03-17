from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

REFERRAL_CODE = "PRANJAL50"
MY_UPI_ID = "pranjal12345786@okaxis"

# Massive Category-wise Inventory
def seed_blinkit_data(db: Session):
    if not db.query(models.Product).first():
        data = [
            # Vegetables
            ("Tomato", "1 kg", 40, 68, "https://cdn.grofers.com/app/images/products/sliding_image/1202a.jpg"),
            ("Onion", "1 kg", 30, 58, "https://cdn.grofers.com/app/images/products/sliding_image/1203a.jpg"),
            ("Potato", "1 kg", 25, 48, "https://cdn.grofers.com/app/images/products/sliding_image/1204a.jpg"),
            # Dairy & Breakfast
            ("Amul Gold Milk", "500 ml", 32, 34, "https://cdn.grofers.com/app/images/products/sliding_image/160a.jpg"),
            ("Harvest Gold Bread", "400 g", 35, 50, "https://cdn.grofers.com/app/images/products/sliding_image/133a.jpg"),
            ("Amul Butter", "100 g", 52, 58, "https://cdn.grofers.com/app/images/products/sliding_image/121a.jpg"),
            # Munchies
            ("Lay's Classic", "50 g", 15, 20, "https://cdn.grofers.com/app/images/products/sliding_image/301a.jpg"),
            ("Maggi Masala", "70 g", 12, 14, "https://cdn.grofers.com/app/images/products/sliding_image/105a.jpg"),
            ("Coca-Cola", "750 ml", 38, 45, "https://cdn.grofers.com/app/images/products/sliding_image/132a.jpg"),
            # Fruits
            ("Banana", "6 pcs", 35, 60, "https://cdn.grofers.com/app/images/products/sliding_image/118a.jpg"),
            ("Apple Royal Gala", "4 pcs", 110, 160, "https://cdn.grofers.com/app/images/products/sliding_image/144a.jpg")
        ]
        for name, unit, m_price, o_price, img in data:
            p = models.Product(name=name, base_unit=unit)
            db.add(p)
            db.commit()
            db.refresh(p)
            db.add_all([
                models.PriceHistory(product_id=p.id, vendor="Azadpur Mandi", price=m_price),
                models.PriceHistory(product_id=p.id, vendor="Blinkit/Zepto", price=o_price)
            ])
        db.commit()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    seed_blinkit_data(db)
    query = request.query_params.get("search", "").capitalize()
    products = db.query(models.Product).filter(models.Product.name.contains(query)).all() if query else db.query(models.Product).all()

    cards = ""
    for p in products:
        mandi = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == p.id, models.PriceHistory.vendor == "Azadpur Mandi").order_by(models.PriceHistory.timestamp.desc()).first()
        online = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == p.id, models.PriceHistory.vendor == "Blinkit/Zepto").order_by(models.PriceHistory.timestamp.desc()).first()
        
        if mandi and online:
            # Mandi images usually use grofers (blinkit) CDN for realism
            img_url = next((x[4] for x in [("Tomato","","","", "https://cdn.grofers.com/app/images/products/sliding_image/1202a.jpg")] if x[0] in p.name), "https://cdn.grofers.com/app/images/products/sliding_image/1202a.jpg")
            
            cards += f"""
            <div class="product-card">
                <div class="discount-badge">{int(((online.price-mandi.price)/online.price)*100)}% OFF</div>
                <img src="{img_url}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/1202/1202125.png'">
                <div class="p-info">
                    <p class="p-name">{p.name}</p>
                    <p class="p-unit">{p.base_unit}</p>
                    <div class="price-row">
                        <div>
                            <span class="mandi-p">₹{mandi.price}</span>
                            <span class="online-p">₹{online.price}</span>
                        </div>
                        <a href="https://www.bigbasket.com/ps/?q={p.name}" class="add-btn">ADD</a>
                    </div>
                </div>
            </div>"""

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{ --blinkit-yellow: #f7d54e; --green: #0c831f; --grey: #828282; }}
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; display: flex; flex-direction: column; }}
            .top-nav {{ background: #fff; padding: 10px 15px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; }}
            .search-container {{ background: #f3f4f6; display: flex; align-items: center; padding: 12px; border-radius: 10px; border: 1px solid #e8e8e8; }}
            .search-container input {{ border: none; background: transparent; outline: none; width: 100%; font-size: 14px; color: #1f1f1f; }}
            .main-layout {{ display: flex; margin-top: 5px; }}
            .sidebar {{ width: 80px; background: #fff; border-right: 1px solid #eee; height: calc(100vh - 120px); position: sticky; top: 75px; }}
            .sidebar-item {{ padding: 15px 5px; text-align: center; font-size: 10px; color: var(--grey); font-weight: 600; border-bottom: 1px solid #f9f9f9; }}
            .sidebar-item.active {{ border-left: 4px solid var(--green); color: var(--green); background: #f0fff0; }}
            .content {{ flex: 1; padding: 10px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .product-card {{ border: 1px solid #eee; border-radius: 12px; padding: 8px; position: relative; }}
            .discount-badge {{ position: absolute; top: 0; left: 0; background: var(--green); color: #fff; font-size: 9px; padding: 2px 6px; border-radius: 12px 0 12px 0; font-weight: bold; }}
            .product-card img {{ width: 100%; height: 100px; object-fit: contain; }}
            .p-name {{ font-size: 13px; font-weight: 600; margin: 5px 0 2px 0; color: #1f1f1f; }}
            .p-unit {{ font-size: 11px; color: var(--grey); margin-bottom: 8px; }}
            .price-row {{ display: flex; justify-content: space-between; align-items: center; }}
            .mandi-p {{ font-weight: 800; font-size: 14px; color: #000; }}
            .online-p {{ font-size: 10px; color: var(--grey); text-decoration: line-through; margin-left: 4px; }}
            .add-btn {{ border: 1px solid var(--green); color: var(--green); padding: 4px 12px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 12px; }}
            .bottom-bar {{ position: fixed; bottom: 0; width: 100%; background: #fff; display: flex; justify-content: space-around; padding: 12px 0; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="top-nav">
            <div style="font-weight: 900; font-size: 18px; margin-bottom: 8px;">Delivery in 10 minutes</div>
            <form action="/" class="search-container">
                <input type="text" name="search" placeholder='Search "paneer"'>
            </form>
        </div>
        <div class="main-layout">
            <div class="sidebar">
                <div class="sidebar-item active">Vegetables</div>
                <div class="sidebar-item">Dairy</div>
                <div class="sidebar-item">Munchies</div>
                <div class="sidebar-item">Fruits</div>
            </div>
            <div class="content">{cards}</div>
        </div>
        <div class="bottom-bar">
            <a href="/" style="text-decoration:none; color:var(--green); font-weight:bold;">Home</a>
            <a href="/premium" style="text-decoration:none; color:var(--grey); font-weight:bold;">Premium</a>
        </div>
    </body>
    </html>
    """
