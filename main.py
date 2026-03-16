from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

app = FastAPI(title="PriceWise AI - All-in-One")

# --- SETTINGS (Yahan apna data dalo) ---
REFERRAL_CODE = "PRANJAL50"  # Aapka BigBasket referral code
MY_UPI_ID = "pranjal12345786@okaxis" # Aapka UPI ID
WHATSAPP_NUMBER = "91XXXXXXXXXX" # Aapka number confirm karne ke liye

@app.get("/", response_class=HTMLResponse)
def dashboard(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    table_rows = ""
    
    for prod in products:
        mandi = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Local Mandi (Sangam Vihar)").order_by(models.PriceHistory.timestamp.desc()).first()
        online = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == prod.id, models.PriceHistory.vendor == "Blinkit/Zepto").order_by(models.PriceHistory.timestamp.desc()).first()

        if mandi and online:
            # Automatic Referral Link for BigBasket
            buy_link = f"https://www.bigbasket.com/ps/?q={prod.name}&referral_code={REFERRAL_CODE}"
            
            table_rows += f"""
            <div class="p-card">
                <div class="mandi-tag">MANDI VERIFIED</div>
                <p class="p-title">{prod.name}</p>
                <div class="p-price-row">
                    <div>
                        <span style="color:#2e7d32; font-weight:bold; font-size:18px;">₹{mandi.price}</span><br>
                        <span style="color:#999; text-decoration:line-through; font-size:11px;">Online: ₹{online.price}</span>
                    </div>
                    <a href="/checkout?item={prod.name}&price={online.price}&link={buy_link}" class="add-button">ADD</a>
                </div>
            </div>
            """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="manifest" href="/manifest.json">
        <style>
            :root {{ --primary: #318616; --bg: #f3f4f6; }}
            body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding-bottom: 80px; }}
            .nav {{ background: #fff; padding: 15px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align:center; }}
            .ad-banner {{ background: #fff3cd; padding: 10px; margin: 10px; border-radius: 10px; font-size: 12px; text-align: center; border: 1px dashed #ffa000; }}
            .product-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 12px; }}
            .p-card {{ background: #fff; border-radius: 15px; padding: 12px; border: 1px solid #eee; }}
            .mandi-tag {{ background: #e8f5e9; color: #2e7d32; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
            .p-title {{ font-size: 15px; font-weight: 600; margin: 8px 0; }}
            .p-price-row {{ display: flex; justify-content: space-between; align-items: center; }}
            .add-button {{ background: #fff; color: var(--primary); border: 1px solid var(--primary); padding: 5px 15px; border-radius: 6px; font-weight: bold; text-decoration: none; }}
            .footer-cart {{ position: fixed; bottom: 0; width: 100%; background: var(--primary); color: #fff; padding: 18px; display: flex; justify-content: space-between; box-sizing: border-box; font-weight: bold; border-radius: 15px 15px 0 0; }}
        </style>
    </head>
    <body>
        <div class="nav"><h2 style="margin:0; color:var(--primary);">PriceWise AI</h2></div>
        <div class="ad-banner">🔥 <b>AD:</b> Get ₹50 OFF on first order! Use code: {REFERRAL_CODE}</div>
        <div class="product-grid">{table_rows}</div>
        <div class="footer-cart">
            <span>🛒 Check Total Savings</span>
            <a href="/premium" style="color:#fff; text-decoration:none;">GO PREMIUM →</a>
        </div>
    </body>
    </html>
    """

@app.get("/checkout", response_class=HTMLResponse)
def checkout(item: str, price: float, link: str):
    return f"""
    <body style="font-family:sans-serif; text-align:center; padding:20px;">
        <h2>🛒 Confirm & Buy</h2>
        <div style="border:1px solid #ddd; padding:20px; border-radius:15px; background:#fff;">
            <h3>{item}</h3>
            <p>Online Price: ₹{price}</p>
            <div style="background:#fff3cd; padding:10px; border-radius:10px; border:1px dashed #ffa000; margin:15px 0;">
                <p style="margin:0; font-size:12px;"><b>SHOPPING AD</b></p>
                <p>Buy 2 Get 1 FREE on Kitchen Spices!</p>
                <button onclick="window.open('https://amazon.in', '_blank')">View Deal</button>
            </div>
        </div>
        <a href="/process-payment" style="display:block; background:#000; color:#fff; padding:15px; margin-top:20px; text-decoration:none; border-radius:10px; font-weight:bold;">Proceed to Buy</a>
    </body>
    """

@app.get("/process-payment", response_class=HTMLResponse)
def payment_ad_transition():
    return """
    <body style="background:#000; color:#fff; text-align:center; padding-top:100px; font-family:sans-serif;">
        <meta http-equiv="refresh" content="4;url=/premium">
        <h3>Securing Checkout...</h3>
        <div style="background:#fff; color:#000; padding:30px; border-radius:20px; width:80%; margin:auto;">
            <p style="color:red; font-weight:bold;">SPONSORED AD</p>
            <img src="https://via.placeholder.com/150x80" alt="ad">
            <h4>New iPhone 15 Pro @ ₹5,999 EMI</h4>
            <button style="padding:10px 20px; background:#007bff; color:#fff; border:none; border-radius:5px;">Check Now</button>
        </div>
        <p>Redirecting to Payment in 4s...</p>
    </body>
    """

@app.get("/premium", response_class=HTMLResponse)
def premium_page():
    qr_data = f"upi://pay?pa={MY_UPI_ID}&pn=PranjalGupta&am=49"
    return f"""
    <body style="font-family:sans-serif; text-align:center; padding:20px; background:#f4f4f4;">
        <div style="background:white; padding:30px; border-radius:20px; box-shadow:0 5px 15px rgba(0,0,0,0.1);">
            <h2 style="color:#318616;">🚀 PriceWise Premium</h2>
            <p>Get Real-time Mandi Alerts & Pro Tips to save ₹500/month</p>
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={qr_data}" style="width:250px; border:5px solid #318616; border-radius:10px;">
            <p><b>Scan to Pay ₹49</b></p>
            <a href="https://wa.me/{WHATSAPP_NUMBER}?text=Hi Pranjal, Maine 49 ka payment kar diya hai" 
               style="display:block; background:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px; font-weight:bold; margin-top:20px;">
               Confirm on WhatsApp
            </a>
        </div>
    </body>
    """
