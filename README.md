# Island Rose Flower Shop – Improved Version

A modern Flask + SQLite flower-shop demo with an animated floral background, centered login page, occasion browsing, 600 seeded products (40 per occasion), cart, checkout, customer orders, and admin product/order pages.

## Run in VS Code

1. Extract the ZIP.
2. Open the extracted `island_rose_flower_shop` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

5. Open **http://127.0.0.1:5000**.

### Easier Windows option
Double-click `run.bat`. It creates the virtual environment, installs dependencies, and starts the app.

## Demo accounts

- Admin: `admin@islandrose.test` / `password`
- Customer: `customer@islandrose.test` / `password`

## Main improvements

- Animated falling flower-petal background across the public pages.
- Centered, glass-style login card.
- Shop-by-occasion section.
- 15 occasions with 40 products each (600 seeded products).
- Search, occasion filter, sorting, product details, cart and checkout.
- Customer order history.
- Admin dashboard, products, orders and customers.
- Responsive design for desktop and mobile.

Product photos use public Unsplash image URLs, so an internet connection is useful for the flower photographs. The animated petal background itself is CSS/JavaScript and does not require a separate video file.


## November 2026 minimal update: original dashboards preserved

- The admin and customer dashboard HTML templates and their layout were not changed.
- Login remains at `/login`, with the existing admin/customer credentials documented above.
- Signed-in customers and admins now have a visible Logout button in the top header.
- Occasion tiles on the home page now show real flower-photo previews.
- Demo catalog products use a curated Unsplash online photo collection. All 40 products **within any one occasion** have 40 different photo sources. Some photos may be reused **across different occasions**, since the shop ships 600 demo listings.
- The database's existing customers, orders, prices, inventory, and product names were preserved; only stock demo photo URLs were refreshed. Custom image URLs added by an admin are not overwritten.
- Photos load from online hosts. An internet connection is required to display them, and host-side availability may change. Photos are representative, not actual stock photos of the shop's inventory. Sources: https://unsplash.com/license.
- The ZIP intentionally excludes `.venv` / `.venv-1`; they are not portable between computers. Run `run.bat` in the same folder as `app.py` on Windows with Python 3.13 installed.

## Admin order viewer and Order Now update

- The existing admin and customer dashboard templates, overall colors, and layout are unchanged.
- Admin **Orders** now lists purchased flower names, quantities, and occasions, with a **View Order** page for full item photos, occasion, quantities, totals, customer, payment and delivery details.
- Customer product cards and product detail pages now offer **Order Now** next to **Add to Cart**. Order Now goes straight to checkout for the chosen product and quantity; it does not add to, clear, or merge with the customer's saved cart.
- The regular cart checkout flow remains available. Payment is simulated; the app does not process real payments.
- The existing SQLite database schema remains unchanged. Existing orders are displayed using their stored order_items records and product information.
