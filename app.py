from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import sqlite3, os, random
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from photo_catalog import PHOTO_COLLECTIONS, OCCASION_THUMBNAILS, ALL_PHOTO_URLS

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "island_rose.db")
app = Flask(__name__)
app.secret_key = "island-rose-demo-secret-key-change-me"

OCCASIONS = [
    ("Birthday", "🎂", "Make their birthday bloom with joy."),
    ("Anniversary", "💕", "Celebrate love that keeps growing."),
    ("Monthsary", "💑", "Sweet flowers for every little milestone."),
    ("Valentine's Day", "❤️", "Romantic blooms made for your favorite person."),
    ("Funeral / Sympathy", "🕊️", "Thoughtful flowers for remembrance and comfort."),
    ("Wedding", "💍", "Elegant flowers for beautiful beginnings."),
    ("Graduation", "🎓", "Celebrate achievement with a bright bouquet."),
    ("Mother's Day", "🌷", "A loving floral thank-you for Mom."),
    ("Father's Day", "🌿", "A fresh and thoughtful gift for Dad."),
    ("Get Well Soon", "🌸", "Send warmth, hope and cheerful blooms."),
    ("Thank You", "🙏", "Say thank you with flowers."),
    ("Congratulations", "🎉", "Celebrate every wonderful achievement."),
    ("Just Because", "🌼", "No occasion needed for a beautiful surprise."),
    ("Romantic / I Love You", "🌹", "Classic romantic arrangements for heartfelt moments."),
    ("More Occasions", "✨", "Explore more beautiful floral gifts."),
]

FLOWER_TYPES = ["Roses", "Tulips", "Sunflowers", "Lilies", "Carnations", "Daisies", "Orchids", "Hydrangeas", "Baby's Breath", "Mixed Flowers"]
COLORS = ["Red", "Pink", "White", "Peach", "Lavender", "Blue", "Yellow", "Cream", "Pastel", "Mixed"]
STYLES = ["Bouquet", "Flower Box", "Basket", "Vase Arrangement", "Luxury Wrap", "Money Bouquet", "Teddy Bear Set", "Gift Set"]
ADJ = ["Classic", "Elegant", "Premium", "Sweet", "Luxury", "Charming", "Dreamy", "Deluxe", "Signature", "Lovely"]

IMAGE_URLS = [
    "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=900&q=85",
    "https://images.unsplash.com/photo-1523438885200-e635ba2c371e?auto=format&fit=crop&w=900&q=85",
    "https://images.unsplash.com/photo-1507504031003-b417219a0fde?auto=format&fit=crop&w=900&q=85",
    "https://images.unsplash.com/photo-1455582916367-25f75bfc6710?auto=format&fit=crop&w=900&q=85",
    "https://images.unsplash.com/photo-1526047932273-341f2a7631f9?auto=format&fit=crop&w=900&q=85",
    "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?auto=format&fit=crop&w=900&q=85",
    "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=900&q=85",
    "https://images.unsplash.com/photo-1560717789-0ac7c58ac90a?auto=format&fit=crop&w=900&q=85",
]


def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c


def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'customer',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        low_stock_limit INTEGER NOT NULL DEFAULT 5,
        image TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        total_amount REAL NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'pending',
        delivery_date TEXT,
        delivery_time TEXT,
        delivery_address TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        subtotal REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS deliveries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE NOT NULL,
        scheduled_date TEXT,
        scheduled_time TEXT,
        status TEXT NOT NULL DEFAULT 'scheduled',
        proof_of_delivery TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
    );
    """)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    accounts = [
        ("Island Rose Admin", "admin@islandrose.test", "password", "admin"),
        ("Demo Customer", "customer@islandrose.test", "password", "customer"),
    ]
    for name, email, pw, role in accounts:
        if not c.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            c.execute("INSERT INTO users(name,email,password,role,created_at) VALUES(?,?,?,?,?)",
                      (name, email, generate_password_hash(pw), role, now))

    count = c.execute("SELECT COUNT(*) x FROM products").fetchone()["x"]
    if count < 500:
        # Seed 40 products for each occasion (600 total) with varied names/prices/images.
        random.seed(20260825)
        for occasion, _, _ in OCCASIONS:
            for i in range(1, 41):
                flower = FLOWER_TYPES[(i - 1) % len(FLOWER_TYPES)]
                color = COLORS[(i * 3) % len(COLORS)]
                style = STYLES[(i * 5) % len(STYLES)]
                adj = ADJ[(i + len(occasion)) % len(ADJ)]
                name = f"{adj} {color} {flower} {style}"
                if occasion == "Valentine's Day":
                    name = f"{adj} {color} Rose {style} – Valentine Collection"
                elif occasion == "Funeral / Sympathy":
                    name = f"{adj} {color} Sympathy {style}"
                elif occasion == "Birthday":
                    name = f"{adj} Birthday {color} {flower} {style}"
                price = 899 + ((i * 137 + len(occasion) * 41) % 1701)
                stock = 8 + (i * 7) % 23
                image = PHOTO_COLLECTIONS[occasion][i - 1]
                desc = f"A thoughtfully arranged {color.lower()} {flower.lower()} {style.lower()} created for {occasion.lower()}. Fresh-looking, gift-ready and beautifully presented by Island Rose."
                c.execute("""INSERT INTO products(name,category,description,price,stock,low_stock_limit,image,is_active,created_at)
                             VALUES(?,?,?,?,?,?,?,?,?)""",
                          (name, occasion, desc, price, stock, 5, image, 1, now))
    # Upgrade only untouched demo-seeded photo links from older versions.
    # Never overwrite images supplied manually by the shop admin.
    for occasion, images in PHOTO_COLLECTIONS.items():
        products = c.execute("SELECT id,image FROM products WHERE category=? ORDER BY id", (occasion,)).fetchall()
        for index, product in enumerate(products):
            if product['image'] in IMAGE_URLS:
                c.execute("UPDATE products SET image=? WHERE id=?", (images[index % len(images)], product['id']))
    c.commit()
    c.close()


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    c = db(); u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone(); c.close()
    return u


@app.context_processor
def inject():
    return {"user": current_user(), "occasions": OCCASIONS, "occasion_thumbnails": OCCASION_THUMBNAILS}


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def staff_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        u = current_user()
        if not u:
            return redirect(url_for("login"))
        if u["role"] not in ("admin", "staff"):
            flash("Staff/Admin access required.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return wrapper


def customer_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        u = current_user()
        if not u:
            return redirect(url_for("login"))
        if u["role"] != "customer":
            flash("Customer access required.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    c = db()
    products = c.execute("SELECT * FROM products WHERE is_active=1 ORDER BY id DESC LIMIT 12").fetchall()
    c.close()
    return render_template("home.html", products=products)


@app.route("/shop")
def shop():
    category = request.args.get("category", "").strip()
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "featured")
    c = db()
    sql = "SELECT * FROM products WHERE is_active=1"
    params = []
    if category:
        sql += " AND category=?"; params.append(category)
    if q:
        sql += " AND (name LIKE ? OR description LIKE ? OR category LIKE ?)"
        like = f"%{q}%"; params += [like, like, like]
    order = {"price_low":"price ASC", "price_high":"price DESC", "newest":"id DESC"}.get(sort, "id DESC")
    sql += f" ORDER BY {order}"
    products = c.execute(sql, params).fetchall()
    c.close()
    return render_template("shop.html", products=products, selected_category=category, q=q, sort=sort)


@app.route("/product/<int:pid>")
def product_detail(pid):
    c = db(); p = c.execute("SELECT * FROM products WHERE id=? AND is_active=1", (pid,)).fetchone(); c.close()
    if not p: abort(404)
    return render_template("product_detail.html", product=p)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pw = request.form.get("password", "")
        c = db(); u = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone(); c.close()
        if u and check_password_hash(u["password"], pw):
            session.clear(); session["user_id"] = u["id"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.post("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    u = current_user(); c = db()
    if u["role"] == "customer":
        orders = c.execute("SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC", (u["id"],)).fetchall()
        c.close(); return render_template("customer_dashboard.html", orders=orders)
    stats = {
        "orders": c.execute("SELECT COUNT(*) x FROM orders").fetchone()["x"],
        "sales": c.execute("SELECT COALESCE(SUM(total_amount),0) x FROM orders WHERE status!='cancelled'").fetchone()["x"],
        "customers": c.execute("SELECT COUNT(*) x FROM users WHERE role='customer'").fetchone()["x"],
        "low": c.execute("SELECT COUNT(*) x FROM products WHERE stock<=low_stock_limit AND is_active=1").fetchone()["x"],
    }
    orders = c.execute("SELECT o.*,u.name customer_name FROM orders o JOIN users u ON u.id=o.customer_id ORDER BY o.id DESC LIMIT 10").fetchall()
    c.close(); return render_template("admin_dashboard.html", stats=stats, orders=orders)


@app.post("/cart/add/<int:pid>")
@customer_required
def add_to_cart(pid):
    qty = max(1, int(request.form.get("quantity", 1)))
    cart = session.get("cart", {})
    cart[str(pid)] = int(cart.get(str(pid), 0)) + qty
    session["cart"] = cart
    flash("Flower added to your cart.", "ok")
    return redirect(request.referrer or url_for("shop"))


@app.post("/order-now/<int:pid>")
@customer_required
def order_now(pid):
    """Start checkout for one product, without modifying the saved cart."""
    try:
        qty = int(request.form.get("quantity", "1"))
    except (TypeError, ValueError):
        qty = 0
    c = db()
    product = c.execute("SELECT id, name, stock FROM products WHERE id=? AND is_active=1", (pid,)).fetchone()
    c.close()
    if not product:
        abort(404)
    if not 1 <= qty <= 99 or qty > product["stock"]:
        flash("Please choose a quantity that is in stock (1–99).", "error")
        return redirect(url_for("product_detail", pid=pid))
    session["buy_now"] = {"product_id": pid, "quantity": qty}
    return redirect(url_for("checkout", mode="now"))


@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    c = db(); items=[]
    for pid, qty in cart.items():
        p = c.execute("SELECT * FROM products WHERE id=? AND is_active=1", (int(pid),)).fetchone()
        if p:
            items.append({"product":p, "quantity":qty, "subtotal":p["price"]*qty})
    c.close(); subtotal=sum(x["subtotal"] for x in items)
    return render_template("cart.html", items=items, subtotal=subtotal, total=subtotal+150)


@app.post("/cart/update")
def update_cart():
    cart = session.get("cart", {})
    for pid in list(cart):
        try: qty = int(request.form.get(f"qty_{pid}", 0))
        except ValueError: qty = 0
        if qty <= 0: cart.pop(pid, None)
        else: cart[pid] = min(qty, 99)
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
@customer_required
def checkout():
    direct_order = request.args.get("mode") == "now"
    c = db(); items = []
    if direct_order:
        pending = session.get("buy_now", {})
        if not isinstance(pending, dict):
            pending = {}
        pid, qty = pending.get("product_id"), pending.get("quantity")
        if type(pid) is int and type(qty) is int and 1 <= qty <= 99:
            product = c.execute("SELECT * FROM products WHERE id=? AND is_active=1", (pid,)).fetchone()
            if product:
                items.append((product, qty))
    else:
        for pid, qty in session.get("cart", {}).items():
            try:
                product_id, quantity = int(pid), int(qty)
            except (ValueError, TypeError):
                continue
            if quantity < 1:
                continue
            product = c.execute("SELECT * FROM products WHERE id=? AND is_active=1", (product_id,)).fetchone()
            if product:
                items.append((product, quantity))
    if not items:
        c.close()
        flash("Select flowers to order before checking out.", "error")
        return redirect(url_for("shop"))
    subtotal=sum(p["price"]*qty for p,qty in items); total=subtotal+150
    if request.method == "POST":
        address=request.form.get("delivery_address", "").strip(); date=request.form.get("delivery_date", ""); tm=request.form.get("delivery_time", "")
        method=request.form.get("payment_method", "GCash")
        if not address or not date or not tm:
            flash("Please complete the delivery information.", "error")
            c.close(); return render_template("checkout.html", items=items, subtotal=subtotal, total=total, direct_order=direct_order)
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            for p,qty in items:
                if p["stock"] < qty: raise ValueError(f"Not enough stock for {p['name']}.")
            oid=c.execute("INSERT INTO orders(customer_id,total_amount,status,delivery_date,delivery_time,delivery_address,created_at) VALUES(?,?,?,?,?,?,?)",
                          (current_user()["id"], total, "processing", date, tm, address, now)).lastrowid
            for p,qty in items:
                sub=p["price"]*qty
                c.execute("INSERT INTO order_items(order_id,product_id,quantity,price,subtotal,created_at) VALUES(?,?,?,?,?,?)",(oid,p["id"],qty,p["price"],sub,now))
                c.execute("UPDATE products SET stock=stock-? WHERE id=?",(qty,p["id"]))
            c.execute("INSERT INTO payments(order_id,payment_method,amount,status,created_at) VALUES(?,?,?,?,?)",(oid,method,total,"pending",now))
            c.execute("INSERT INTO deliveries(order_id,scheduled_date,scheduled_time,status,created_at) VALUES(?,?,?,?,?)",(oid,date,tm,"scheduled",now))
            c.commit()
            if direct_order:
                session.pop("buy_now", None)
            else:
                session["cart"] = {}
            c.close()
            return redirect(url_for("order_success", oid=oid))
        except Exception as e:
            c.rollback(); c.close(); flash(str(e), "error")
    else:
        c.close()
    return render_template("checkout.html", items=items, subtotal=subtotal, total=total, direct_order=direct_order)


@app.route("/order-success/<int:oid>")
@customer_required
def order_success(oid):
    return render_template("order_success.html", oid=oid)


@app.route("/products", methods=["GET","POST"])
@staff_required
def products_admin():
    c=db()
    if request.method == "POST":
        name=request.form.get("name","").strip(); category=request.form.get("category","").strip(); desc=request.form.get("description","").strip()
        try: price=float(request.form.get("price",0)); stock=int(request.form.get("stock",0))
        except ValueError: price=-1; stock=-1
        if not name or not category or price < 0 or stock < 0:
            flash("Please enter valid product information.", "error")
        else:
            now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            image = request.form.get("image", "").strip()
            if not image:
                used = {row["image"] for row in c.execute("SELECT image FROM products WHERE category=? AND is_active=1", (category,))}
                image = next((url for url in ALL_PHOTO_URLS if url not in used),
                             PHOTO_COLLECTIONS.get(category, PHOTO_COLLECTIONS["More Occasions"])[0])
            c.execute("INSERT INTO products(name,category,description,price,stock,low_stock_limit,image,is_active,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                      (name,category,desc,price,stock,5,image,1,now)); c.commit(); flash("Product added.","ok")
        c.close(); return redirect(url_for("products_admin"))
    products=c.execute("SELECT * FROM products ORDER BY id DESC LIMIT 100").fetchall(); c.close()
    return render_template("products_admin.html", products=products)


@app.post("/products/<int:pid>/archive")
@staff_required
def archive_product(pid):
    c=db(); c.execute("UPDATE products SET is_active=0 WHERE id=?",(pid,)); c.commit(); c.close(); return redirect(url_for("products_admin"))


@app.route("/orders")
@staff_required
def orders_admin():
    c = db()
    orders = c.execute("""
        SELECT o.*, u.name AS customer_name, pay.status AS payment_status
        FROM orders o
        JOIN users u ON u.id = o.customer_id
        LEFT JOIN payments pay ON pay.id = (
            SELECT id FROM payments WHERE order_id = o.id ORDER BY id DESC LIMIT 1
        )
        ORDER BY o.id DESC
    """).fetchall()
    # Stored order_items links each purchase to the flower and its occasion.
    rows = c.execute("""
        SELECT oi.order_id, oi.quantity, p.name AS flower_name, p.category AS occasion
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        ORDER BY oi.order_id DESC, oi.id
    """).fetchall()
    items_by_order = {}
    for item in rows:
        items_by_order.setdefault(item["order_id"], []).append(item)
    c.close()
    return render_template("orders_admin.html", orders=orders, items_by_order=items_by_order)


@app.get("/orders/<int:oid>")
@staff_required
def order_detail_admin(oid):
    c = db()
    order = c.execute("""
        SELECT o.*, u.name AS customer_name, u.email AS customer_email,
               pay.payment_method, pay.status AS payment_status
        FROM orders o
        JOIN users u ON u.id = o.customer_id
        LEFT JOIN payments pay ON pay.id = (
            SELECT id FROM payments WHERE order_id = o.id ORDER BY id DESC LIMIT 1
        )
        WHERE o.id = ?
    """, (oid,)).fetchone()
    if not order:
        c.close()
        abort(404)
    items = c.execute("""
        SELECT oi.quantity, oi.price, oi.subtotal, p.name AS flower_name,
               p.category AS occasion, p.image AS flower_image
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id = ? ORDER BY oi.id
    """, (oid,)).fetchall()
    c.close()
    return render_template("order_detail_admin.html", order=order, items=items)


@app.post("/orders/<int:oid>/status")
@staff_required
def order_status(oid):
    status=request.form.get("status", "processing")
    c=db(); c.execute("UPDATE orders SET status=? WHERE id=?",(status,oid)); c.commit(); c.close(); return redirect(url_for("orders_admin"))


@app.route("/customers")
@staff_required
def customers():
    c=db(); rows=c.execute("SELECT u.name,u.email,COUNT(o.id) orders_count,COALESCE(SUM(o.total_amount),0) total_spent FROM users u LEFT JOIN orders o ON o.customer_id=u.id WHERE u.role='customer' GROUP BY u.id ORDER BY u.id DESC").fetchall(); c.close()
    return render_template("customers.html", customers=rows)


if __name__ == "__main__":
    init_db()
    print("\n🌹 Island Rose Flower Shop -> http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
