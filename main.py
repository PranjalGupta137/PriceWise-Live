from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# Tables automatically banao
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PriceWise AI")

MY_UPI_ID = "yourname@upi"  # APNA UPI ID YAHAN DALEIN
WHATSAPP = "919999999999"   # APNA WHATSAPP NUMBER

# =============================================================
# MEGA INVENTORY — 100+ Products, Real Images, Multi-App Prices
# Format: (Name, Unit, Blinkit, Zepto, BigBasket, Swiggy, Image_URL)
# =============================================================
MEGA_DATA = [
    # --- VEGETABLES ---
    ("Tomato", "1 kg", 68, 72, 62, 70, "https://images.unsplash.com/photo-1561136594-7f68af7569b5?w=200&q=80"),
    ("Onion", "1 kg", 55, 58, 50, 56, "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=200&q=80"),
    ("Potato", "1 kg", 45, 48, 42, 46, "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=200&q=80"),
    ("Ginger", "100 g", 25, 28, 22, 26, "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?w=200&q=80"),
    ("Garlic", "100 g", 35, 38, 32, 36, "https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=200&q=80"),
    ("Lemon", "4 pcs", 20, 22, 18, 20, "https://images.unsplash.com/photo-1590502593747-42a996133562?w=200&q=80"),
    ("Spinach", "200 g", 22, 25, 20, 24, "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=200&q=80"),
    ("Green Chilli", "100 g", 15, 18, 14, 16, "https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=200&q=80"),
    ("Capsicum", "250 g", 30, 32, 28, 31, "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=200&q=80"),
    ("Coriander", "50 g", 10, 12, 9, 11, "https://images.unsplash.com/photo-1553557231-f9a6e6b77c0e?w=200&q=80"),
    ("Brinjal", "500 g", 25, 28, 22, 26, "https://images.unsplash.com/photo-1615484477778-ca3b77940c25?w=200&q=80"),
    ("Peas", "250 g", 35, 38, 32, 36, "https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=200&q=80"),

    # --- FRUITS ---
    ("Apple", "4 pcs", 140, 155, 135, 148, "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?w=200&q=80"),
    ("Banana", "6 pcs", 35, 40, 32, 38, "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=200&q=80"),
    ("Grapes", "500 g", 75, 80, 70, 78, "https://images.unsplash.com/photo-1596363505729-4190a9506133?w=200&q=80"),
    ("Papaya", "1 pc", 50, 55, 48, 52, "https://images.unsplash.com/photo-1526318896980-cf78c088247c?w=200&q=80"),
    ("Watermelon", "1 pc", 80, 90, 75, 85, "https://images.unsplash.com/photo-1563114773-84221bd62daa?w=200&q=80"),
    ("Orange", "4 pcs", 55, 60, 52, 58, "https://images.unsplash.com/photo-1547514701-42782101795e?w=200&q=80"),
    ("Pomegranate", "2 pcs", 90, 95, 88, 92, "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=200&q=80"),
    ("Mango", "1 kg", 120, 130, 115, 125, "https://images.unsplash.com/photo-1553279768-865429fa0078?w=200&q=80"),

    # --- DAIRY & BREAKFAST ---
    ("Amul Gold Milk", "500 ml", 34, 34, 33, 35, "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=200&q=80"),
    ("Mother Dairy Milk", "500 ml", 28, 28, 27, 29, "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=200&q=80"),
    ("Amul Paneer", "200 g", 90, 95, 88, 92, "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=200&q=80"),
    ("Amul Butter", "100 g", 58, 58, 56, 60, "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=200&q=80"),
    ("Amul Cheese Slices", "200 g", 115, 118, 112, 116, "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=200&q=80"),
    ("Curd", "400 g", 38, 40, 36, 39, "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=200&q=80"),
    ("Bread White", "400 g", 42, 45, 40, 44, "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=200&q=80"),
    ("Brown Bread", "400 g", 48, 50, 46, 49, "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=200&q=80"),
    ("Eggs", "6 pcs", 58, 60, 55, 59, "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=200&q=80"),
    ("Cornflakes", "300 g", 88, 92, 85, 90, "https://images.unsplash.com/photo-1521483451569-e33803c0330c?w=200&q=80"),

    # --- GROCERY (DRY GOODS) ---
    ("Aashirvaad Atta", "5 kg", 225, 232, 218, 228, "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=200&q=80"),
    ("Basmati Rice", "1 kg", 85, 90, 82, 88, "https://images.unsplash.com/photo-1536304993881-ff86e0c9b65b?w=200&q=80"),
    ("Sugar", "1 kg", 45, 48, 43, 46, "https://images.unsplash.com/photo-1559548331-f9cb98001426?w=200&q=80"),
    ("Tata Salt", "1 kg", 22, 24, 21, 23, "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=200&q=80"),
    ("Toor Dal", "1 kg", 115, 120, 110, 118, "https://images.unsplash.com/photo-1515543904379-3d757abe528f?w=200&q=80"),
    ("Moong Dal", "500 g", 65, 68, 62, 66, "https://images.unsplash.com/photo-1515543904379-3d757abe528f?w=200&q=80"),
    ("Fortune Sunflower Oil", "1 L", 130, 135, 128, 132, "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=200&q=80"),
    ("Haldi", "100 g", 28, 30, 26, 29, "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=200&q=80"),

    # --- SNACKS & MUNCHIES ---
    ("Maggi 2-Minute", "70 g", 14, 14, 13, 14, "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=200&q=80"),
    ("Lay's Classic Salted", "78 g", 20, 20, 18, 20, "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=200&q=80"),
    ("Kurkure Masala Munch", "60 g", 20, 20, 18, 20, "https://images.unsplash.com/photo-1562907550-096d3bf9b25c?w=200&q=80"),
    ("Haldiram Bhujia", "150 g", 65, 68, 62, 66, "https://images.unsplash.com/photo-1562907550-096d3bf9b25c?w=200&q=80"),
    ("Dark Fantasy Biscuits", "75 g", 28, 30, 26, 29, "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=200&q=80"),
    ("Oreo", "120 g", 38, 40, 36, 39, "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=200&q=80"),
    ("Good Day Cashew", "87 g", 20, 22, 18, 21, "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=200&q=80"),
    ("Act II Popcorn", "30 g", 25, 28, 23, 26, "https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=200&q=80"),

    # --- COLD DRINKS & JUICES ---
    ("Coca-Cola", "750 ml", 42, 42, 38, 42, "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=200&q=80"),
    ("Pepsi", "750 ml", 42, 42, 38, 42, "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=200&q=80"),
    ("Sprite", "750 ml", 42, 42, 38, 42, "https://images.unsplash.com/photo-1625772452859-1c03d884dcd7?w=200&q=80"),
    ("Thums Up", "750 ml", 42, 42, 38, 42, "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=200&q=80"),
    ("Maaza Mango Drink", "600 ml", 38, 40, 35, 39, "https://images.unsplash.com/photo-1534353436294-0dbd4bdac845?w=200&q=80"),
    ("Real Orange Juice", "1 L", 115, 120, 110, 118, "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=200&q=80"),
    ("Red Bull", "250 ml", 115, 118, 112, 116, "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=200&q=80"),
    ("Bisleri Water", "1 L", 18, 18, 16, 18, "https://images.unsplash.com/photo-1568162486098-b5de3f06c8b5?w=200&q=80"),

    # --- PERSONAL CARE ---
    ("Dove Soap", "100 g", 45, 48, 43, 46, "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=200&q=80"),
    ("Colgate MaxFresh", "150 g", 88, 90, 85, 89, "https://images.unsplash.com/photo-1559591935-c92d56a67aba?w=200&q=80"),
    ("Head & Shoulders", "340 ml", 280, 285, 275, 282, "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=200&q=80"),
    ("Dettol Handwash", "200 ml", 65, 68, 62, 66, "https://images.unsplash.com/photo-1584515933487-779824d29309?w=200&q=80"),
    ("Parachute Hair Oil", "200 ml", 105, 110, 100, 108, "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=200&q=80"),

    # --- INSTANT FOOD ---
    ("Yippee Noodles", "70 g", 14, 14, 13, 14, "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=200&q=80"),
    ("McCain French Fries", "420 g", 155, 160, 150, 158, "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=200&q=80"),
    ("Knorr Tomato Soup", "50 g", 38, 40, 36, 39, "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=200&q=80"),
]

# Category mapping for sidebar
CATEGORIES = {
    "All": None,
    "Vegetables": ["Tomato","Onion","Potato","Ginger","Garlic","Lemon","Spinach","Green Chilli","Capsicum","Coriander","Brinjal","Peas"],
    "Fruits": ["Apple","Banana","Grapes","Papaya","Watermelon","Orange","Pomegranate","Mango"],
    "Dairy": ["Milk","Paneer","Butter","Cheese","Curd","Bread","Eggs","Cornflakes"],
    "Grocery": ["Atta","Rice","Sugar","Salt","Dal","Oil","Haldi"],
    "Snacks": ["Maggi","Lay's","Kurkure","Haldiram","Dark Fantasy","Oreo","Good Day","Act II","Popcorn"],
    "Drinks": ["Coca-Cola","Pepsi","Sprite","Thums Up","Maaza","Juice","Red Bull","Bisleri"],
    "Care": ["Dove","Colgate","Head","Dettol","Parachute"],
    "Instant": ["Yippee","McCain","Knorr"],
}

def seed_data(db: Session):
    if not db.query(models.Product).first():
        for name, unit, b_p, z_p, bb_p, sw_p, img in MEGA_DATA:
            p = models.Product(name=name, base_unit=unit)
            db.add(p)
            db.commit()
            db.refresh(p)
            db.add_all([
                models.PriceHistory(product_id=p.id, vendor="Blinkit", price=b_p),
                models.PriceHistory(product_id=p.id, vendor="Zepto", price=z_p),
                models.PriceHistory(product_id=p.id, vendor="BigBasket", price=bb_p),
                models.PriceHistory(product_id=p.id, vendor="Swiggy Instamart", price=sw_p),
            ])
        db.commit()

def get_img(name):
    for item in MEGA_DATA:
        if item[0] == name:
            return item[6]
    return "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=200&q=80"

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    seed_data(db)
    query = request.query_params.get("q", "")
    cat = request.query_params.get("cat", "All")

    all_products = db.query(models.Product).all()

    if query:
        products = [p for p in all_products if query.lower() in p.name.lower()]
    elif cat != "All" and cat in CATEGORIES:
        keywords = CATEGORIES[cat]
        products = [p for p in all_products if any(k.lower() in p.name.lower() for k in keywords)]
    else:
        products = all_products

    VENDOR_COLORS = {
        "Blinkit": "#f7d54e",
        "Zepto": "#8b5cf6",
        "BigBasket": "#16a34a",
        "Swiggy Instamart": "#f97316",
    }
    VENDOR_LINKS = {
        "Blinkit": "https://blinkit.com/s/?q=",
        "Zepto": "https://zeptonow.com/search?query=",
        "BigBasket": "https://www.bigbasket.com/ps/?q=",
        "Swiggy Instamart": "https://www.swiggy.com/search?query=",
    }

    cards = ""
    for p in products:
        prices_rows = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == p.id).all()
        if not prices_rows:
            continue
        price_map = {pr.vendor: pr.price for pr in prices_rows}
        cheapest = min(price_map, key=price_map.get)
        cheapest_price = price_map[cheapest]
        most_expensive = max(price_map.values())
        savings = int(most_expensive - cheapest_price)
        img = get_img(p.name)

        vendor_rows = ""
        for vendor, price in sorted(price_map.items(), key=lambda x: x[1]):
            is_best = vendor == cheapest
            color = VENDOR_COLORS.get(vendor, "#666")
            link = VENDOR_LINKS.get(vendor, "#") + p.name.replace(" ", "+")
            best_tag = '<span class="best-tag">BEST</span>' if is_best else ""
            vendor_rows += f"""
            <a href="{link}" target="_blank" class="vendor-row {'vendor-best' if is_best else ''}">
                <span class="vendor-name" style="color:{color};">{vendor}</span>
                {best_tag}
                <span class="vendor-price" style="color:{'#000' if is_best else '#777'}; font-weight:{'800' if is_best else '400'}">₹{price}</span>
            </a>"""

        cards += f"""
        <div class="card">
            <div class="save-badge">SAVE ₹{savings}</div>
            <img src="{img}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=200&q=80'">
            <div class="card-body">
                <p class="product-name">{p.name}</p>
                <p class="product-unit">{p.base_unit}</p>
                <div class="vendor-list">{vendor_rows}</div>
            </div>
        </div>"""

    sidebar_items = ""
    for c in CATEGORIES:
        active = "active" if c == cat else ""
        sidebar_items += f'<a href="/?cat={c}" class="sidebar-item {active}">{c}</a>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PriceWise — Compare Grocery Prices</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
:root {{
    --yellow: #f7d54e;
    --green: #0c831f;
    --bg: #f8f9fb;
    --white: #ffffff;
    --border: #ebebeb;
    --text: #1a1a1a;
    --muted: #888;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); }}

/* TOP NAV */
.topnav {{
    background: var(--yellow);
    padding: 14px 20px;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}
.topnav-inner {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.brand {{
    font-size: 20px;
    font-weight: 900;
    color: #000;
    white-space: nowrap;
    text-decoration: none;
}}
.search-wrap {{
    flex: 1;
    position: relative;
}}
.search-wrap form {{
    display: flex;
}}
.search-input {{
    width: 100%;
    border: 2px solid #fff;
    background: #fff;
    padding: 10px 16px;
    border-radius: 10px;
    font-size: 15px;
    font-family: 'DM Sans', sans-serif;
    outline: none;
    font-weight: 500;
}}
.search-input:focus {{ border-color: var(--green); }}

/* LAYOUT */
.layout {{ display: flex; min-height: calc(100vh - 60px); }}

/* SIDEBAR */
.sidebar {{
    width: 90px;
    background: var(--white);
    border-right: 1px solid var(--border);
    position: sticky;
    top: 60px;
    height: calc(100vh - 60px);
    overflow-y: auto;
    flex-shrink: 0;
}}
.sidebar-item {{
    display: block;
    padding: 14px 6px;
    text-align: center;
    font-size: 11px;
    font-weight: 700;
    color: var(--muted);
    text-decoration: none;
    border-bottom: 1px solid var(--border);
    transition: 0.15s;
    letter-spacing: 0.3px;
}}
.sidebar-item:hover {{ background: #f0f0f0; color: var(--text); }}
.sidebar-item.active {{
    border-left: 3px solid var(--green);
    color: var(--green);
    background: #f0fff0;
}}

/* PRODUCT GRID */
.main-content {{ flex: 1; padding: 14px; overflow: hidden; }}
.section-title {{
    font-size: 13px;
    font-weight: 700;
    color: var(--muted);
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
    gap: 12px;
}}

/* CARD */
.card {{
    background: var(--white);
    border-radius: 16px;
    border: 1px solid var(--border);
    overflow: hidden;
    position: relative;
    transition: box-shadow 0.2s;
}}
.card:hover {{ box-shadow: 0 6px 20px rgba(0,0,0,0.08); }}
.save-badge {{
    position: absolute;
    top: 0; left: 0;
    background: var(--green);
    color: #fff;
    font-size: 9px;
    font-weight: 900;
    padding: 3px 9px;
    border-radius: 16px 0 16px 0;
    letter-spacing: 0.4px;
}}
.card img {{
    width: 100%;
    height: 120px;
    object-fit: cover;
    display: block;
    background: #f3f3f3;
}}
.card-body {{ padding: 10px; }}
.product-name {{
    font-weight: 800;
    font-size: 13px;
    margin-bottom: 2px;
    line-height: 1.3;
}}
.product-unit {{
    font-size: 11px;
    color: var(--muted);
    margin-bottom: 10px;
}}
.vendor-list {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}
.vendor-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 8px;
    border-radius: 8px;
    background: #fafafa;
    border: 1px solid #f0f0f0;
    text-decoration: none;
    transition: 0.15s;
    gap: 4px;
}}
.vendor-row:hover {{ transform: scale(1.02); border-color: #ddd; }}
.vendor-best {{
    background: #f0fff0;
    border-color: #c6f0c6;
}}
.vendor-name {{ font-size: 10px; font-weight: 700; flex: 1; }}
.vendor-price {{ font-size: 12px; }}
.best-tag {{
    background: var(--green);
    color: #fff;
    font-size: 8px;
    font-weight: 900;
    padding: 1px 5px;
    border-radius: 4px;
    letter-spacing: 0.3px;
}}

/* EMPTY STATE */
.empty {{ text-align: center; padding: 60px 20px; color: var(--muted); grid-column: 1/-1; }}
.empty h2 {{ font-size: 20px; margin-bottom: 8px; }}

/* MOBILE */
@media (max-width: 600px) {{
    .sidebar {{ width: 70px; }}
    .sidebar-item {{ font-size: 9px; padding: 12px 4px; }}
    .grid {{ grid-template-columns: 1fr 1fr; gap: 8px; }}
    .card img {{ height: 100px; }}
}}
</style>
</head>
<body>

<nav class="topnav">
    <div class="topnav-inner">
        <a href="/" class="brand">⚡ PriceWise</a>
        <div class="search-wrap">
            <form action="/" method="get">
                <input class="search-input" type="text" name="q" value="{query}" placeholder='Search "Milk", "Maggi", "Apple"...'>
            </form>
        </div>
    </div>
</nav>

<div class="layout">
    <nav class="sidebar">{sidebar_items}</nav>
    <main class="main-content">
        <p class="section-title">{len(products)} products — Compare prices across 4 apps</p>
        <div class="grid">
            {cards if cards else '<div class="empty"><h2>🔍 No products found</h2><p>Try searching something else</p></div>'}
        </div>
    </main>
</div>

</body>
</html>"""


@app.get("/premium", response_class=HTMLResponse)
def premium():
    qr_data = f"upi://pay?pa={MY_UPI_ID}&pn=PriceWise&am=49"
    return f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700;900&display=swap" rel="stylesheet">
<style>
body {{ font-family: 'DM Sans', sans-serif; background: #f8f9fb; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0; padding:20px; }}
.card {{ background:#fff; padding:36px; border-radius:24px; box-shadow:0 12px 40px rgba(0,0,0,0.12); text-align:center; max-width:340px; width:100%; }}
h1 {{ font-size:28px; font-weight:900; color:#0c831f; margin-bottom:8px; }}
p {{ color:#666; font-size:14px; margin-bottom:24px; }}
.qr {{ border:4px solid #0c831f; border-radius:16px; width:200px; height:200px; margin:0 auto 20px; }}
.wa-btn {{ display:block; background:#25D366; color:#fff; padding:14px; border-radius:12px; text-decoration:none; font-weight:800; font-size:15px; }}
.back {{ display:block; margin-top:14px; color:#888; font-size:13px; text-decoration:none; }}
</style>
</head>
<body>
<div class="card">
    <h1>⚡ Premium Alerts</h1>
    <p>Get daily price drop alerts on WhatsApp. Pay ₹49/month.</p>
    <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}" class="qr">
    <p><strong>Scan to Pay ₹49</strong></p>
    <a href="https://wa.me/{WHATSAPP}?text=Hi%2C+I+paid+for+PriceWise+Premium+%E2%9A%A1" class="wa-btn">✅ Confirm on WhatsApp</a>
    <a href="/" class="back">← Back to App</a>
</div>
</body>
</html>"""
