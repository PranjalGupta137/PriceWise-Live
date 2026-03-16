from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def dashboard(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    table_rows = ""
    
    for prod in products:
        mandi = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Local Mandi (Sangam Vihar)").order_by(models.PriceHistory.timestamp.desc()).first()
        online = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Blinkit/Zepto").order_by(models.PriceHistory.timestamp.desc()).first()

        if mandi and online:
            # Direct Search Links (Trust build karne ke liye)
            blinkit_link = f"https://blinkit.com/s/?q={prod.name}"
            
            table_rows += f"""
            <div class="card">
                <div class="mandi-badge">SANGAM VIHAR MANDI</div>
                <p class="title">{prod.name}</p>
                <div class="price-row">
                    <span class="m-price">₹{mandi.price}</span>
                    <span class="o-price">Online: ₹{online.price}</span>
                </div>
                <div style="margin-top:10px; font-size:11px; color:#27ae60; font-weight:bold;">
                    You Save: ₹{round(online.price - mandi.price, 1)} per kg!
                </div>
                <a href="{blinkit_link}" target="_blank" class="buy-btn">Order Online</a>
            </div>"""

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{ --primary: #318616; --bg: #f3f4f6; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: var(--bg); padding-bottom: 80px; }}
            .nav {{ background: #fff; padding: 15px; position: sticky; top:0; z-index:100; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }}
            .card {{ background: #fff; border-radius: 12px; padding: 12px; border: 1px solid #eee; }}
            .mandi-badge {{ background: #fff3cd; color: #856404; font-size: 9px; padding: 2px 5px; border-radius: 4px; font-weight: bold; }}
            .title {{ font-size: 15px; font-weight: 700; margin: 8px 0; }}
            .m-price {{ color: #1e1e1e; font-weight: bold; font-size: 18px; display: block; }}
            .o-price {{ color: #888; text-decoration: line-through; font-size: 11px; }}
            .buy-btn {{ display: block; text-align: center; background: var(--primary); color: #fff; padding: 8px; border-radius: 6px; font-weight: bold; text-decoration: none; margin-top: 10px; font-size: 13px; }}
            .footer {{ position: fixed; bottom: 0; width: 100%; background: #000; color: #fff; padding: 15px; text-align: center; font-weight: bold; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="nav"><h2 style="margin:0; color:var(--primary);">PriceWise AI</h2></div>
        <div class="grid">{table_rows}</div>
        <div class="footer">🚀 CHECK DAILY MANDI RATES & SAVE!</div>
    </body>
    </html>"""