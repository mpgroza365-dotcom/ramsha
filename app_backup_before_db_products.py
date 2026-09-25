from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from datetime import timedelta

app = Flask(__name__)

# =========================================================
# SESSION
# =========================================================

app.secret_key = "ramsha_v2_secret_key"
ADMIN_PASSWORD = "Ramsha@2026"


app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False


# =========================================================
# PRODUCTS
# =========================================================

PRODUCTS = [
    {
        "id": 1,
        "name": "Red Bull",
        "price": 250,
        "store": "سوبر ماركت",
        "category": "مشروبات",
        "image": "https://images.unsplash.com/photo-1622543925917-763c34d1a86e?w=600"
    },
    {
        "id": 2,
        "name": "برغر لحم",
        "price": 850,
        "store": "مطاعم رمشة",
        "category": "مطاعم",
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600"
    },
    {
        "id": 3,
        "name": "بيتزا",
        "price": 1200,
        "store": "مطاعم رمشة",
        "category": "مطاعم",
        "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=600"
    },
    {
        "id": 4,
        "name": "منتج صيدلية",
        "price": 500,
        "store": "صيدلية رمشة",
        "category": "صيدلية",
        "image": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=600"
    }
]


# =========================================================
# CATEGORIES
# =========================================================

CATEGORIES = [
    {"name": "الكل", "icon": "✨"},
    {"name": "مطاعم", "icon": "🍔"},
    {"name": "صيدلية", "icon": "💊"},
    {"name": "سوبر ماركت", "icon": "🛒"},
    {"name": "مشروبات", "icon": "🥤"}
]


# =========================================================
# SESSION CART
# =========================================================

def get_product(product_id):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product

    return None


def get_cart():
    cart = session.get("cart")

    if not isinstance(cart, dict):
        cart = {}

    return cart


def cart_count():
    cart = get_cart()

    return sum(cart.values())


def cart_total():
    total = 0

    for product_id, quantity in get_cart().items():

        product = get_product(int(product_id))

        if product:
            total += product["price"] * quantity

    return total


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        products=PRODUCTS,
        categories=CATEGORIES,
        cart_count=cart_count()
    )


# =========================================================
# CART PAGE
# =========================================================

@app.route("/cart")
def cart():

    items = []

    for product_id, quantity in get_cart().items():

        product = get_product(int(product_id))

        if not product:
            continue

        items.append({
            "product": product,
            "quantity": quantity,
            "item_total": product["price"] * quantity
        })

    subtotal = sum(
        item["item_total"]
        for item in items
    )

    delivery_fee = 0 if not items else 100

    grand_total = subtotal + delivery_fee

    return render_template(
        "cart.html",
        items=items,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        grand_total=grand_total,
        cart_count=cart_count()
    )


# =========================================================
# ADD TO CART
# =========================================================

@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    product = get_product(product_id)

    if not product:

        return jsonify({
            "success": False,
            "message": "المنتج غير موجود"
        }), 404

    cart = get_cart()

    key = str(product_id)

    cart[key] = cart.get(key, 0) + 1

    session["cart"] = cart

    # مهم جدًا
    session.permanent = True
    session.modified = True

    return jsonify({
        "success": True,
        "cart_count": cart_count()
    })


# =========================================================
# INCREASE
# =========================================================

@app.route("/cart/increase/<int:product_id>", methods=["POST"])
def increase_cart(product_id):

    cart = get_cart()

    key = str(product_id)

    if key in cart:
        cart[key] += 1

    session["cart"] = cart
    session.permanent = True
    session.modified = True

    return redirect(url_for("cart"))


# =========================================================
# DECREASE
# =========================================================

@app.route("/cart/decrease/<int:product_id>", methods=["POST"])
def decrease_cart(product_id):

    cart = get_cart()

    key = str(product_id)

    if key in cart:

        cart[key] -= 1

        if cart[key] <= 0:
            del cart[key]

    session["cart"] = cart
    session.permanent = True
    session.modified = True

    return redirect(url_for("cart"))


# =========================================================
# REMOVE
# =========================================================

@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):

    cart = get_cart()

    key = str(product_id)

    if key in cart:
        del cart[key]

    session["cart"] = cart
    session.permanent = True
    session.modified = True

    return redirect(url_for("cart"))


# =========================================================
# CLEAR CART
# =========================================================

@app.route("/cart/clear", methods=["POST"])
def clear_cart():

    session["cart"] = {}

    session.permanent = True
    session.modified = True

    return redirect(url_for("cart"))


# =========================================================
# CART API
# =========================================================


# =========================================================
# CHECKOUT
# =========================================================

@app.route("/checkout")
def checkout():

    if not get_cart():
        return redirect(url_for("cart"))

    subtotal = cart_total()
    delivery_fee = 100
    grand_total = subtotal + delivery_fee

    return render_template(
        "checkout.html",
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        grand_total=grand_total,
        cart_count=cart_count()
    )


@app.route("/admin/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    import sqlite3

    status = request.form.get("status", "").strip()

    allowed_statuses = {
        "جديد",
        "قيد التجهيز",
        "تم التوصيل",
        "ملغي"
    }

    if status not in allowed_statuses:
        return redirect(url_for("admin_orders"))

    conn = sqlite3.connect("orders.db")

    conn.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_orders"))


@app.route("/order/<int:order_id>")
def order_tracking(order_id):
    import sqlite3

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row

    order = conn.execute(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (order_id, user_id)
    ).fetchone()

    if not order:
        conn.close()
        return "الطلب غير موجود", 404

    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id = ?",
        (order_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "order.html",
        order=order,
        items=items
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    import sqlite3
    from werkzeug.security import generate_password_hash

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not phone or not password:
            return render_template(
                "register.html",
                error="يرجى تعبئة جميع الحقول"
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                error="كلمة المرور يجب أن تكون 6 أحرف على الأقل"
            )

        if password != confirm_password:
            return render_template(
                "register.html",
                error="كلمتا المرور غير متطابقتين"
            )

        conn = sqlite3.connect("orders.db")

        existing = conn.execute(
            "SELECT id FROM users WHERE phone = ?",
            (phone,)
        ).fetchone()

        if existing:
            conn.close()
            return render_template(
                "register.html",
                error="رقم الهاتف مسجل مسبقًا"
            )

        password_hash = generate_password_hash(password)

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (name, phone, password_hash)
            VALUES (?, ?, ?)
        """, (
            name,
            phone,
            password_hash
        ))

        user_id = cur.lastrowid

        conn.commit()
        conn.close()

        session["user_id"] = user_id
        session["user_name"] = name

        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    import sqlite3
    from werkzeug.security import check_password_hash

    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        conn = sqlite3.connect("orders.db")
        conn.row_factory = sqlite3.Row

        user = conn.execute(
            "SELECT * FROM users WHERE phone = ?",
            (phone,)
        ).fetchone()

        conn.close()

        if not user or not check_password_hash(
            user["password_hash"],
            password
        ):
            return render_template(
                "login.html",
                error="رقم الهاتف أو كلمة المرور غير صحيحة"
            )

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)

    return redirect(url_for("home"))

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            session.permanent = True
            return redirect(url_for("admin_orders"))

        return render_template(
            "admin_login.html",
            error="كلمة المرور غير صحيحة"
        )

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/orders")
def admin_orders():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    import sqlite3

    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row

    orders_rows = conn.execute("""
        SELECT *
        FROM orders
        ORDER BY id DESC
    """).fetchall()

    orders = []

    for order in orders_rows:
        items_rows = conn.execute("""
            SELECT *
            FROM order_items
            WHERE order_id = ?
        """, (order["id"],)).fetchall()

        order_data = dict(order)
        order_data["items"] = [dict(item) for item in items_rows]
        orders.append(order_data)

    conn.close()

    return render_template(
        "admin_orders.html",
        orders=orders
    )


@app.route("/account")
def account():
    import sqlite3

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row

    user = conn.execute(
        "SELECT id, name, phone, created_at FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    order_count = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]

    recent_orders = conn.execute("""
        SELECT id, grand_total, status, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 3
    """, (user_id,)).fetchall()

    conn.close()

    if not user:
        session.pop("user_id", None)
        session.pop("user_name", None)
        return redirect(url_for("login"))

    return render_template(
        "account.html",
        user=user,
        order_count=order_count,
        recent_orders=recent_orders
    )


@app.route("/orders")
def my_orders():
    import sqlite3

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row

    orders = conn.execute("""
        SELECT *
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return render_template("orders.html", orders=orders)


@app.route("/api/order", methods=["POST"])
def create_order():
    import sqlite3

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "success": False,
            "message": "يرجى تسجيل الدخول أولاً"
        }), 401

    data = request.get_json() or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    address = str(data.get("address", "")).strip()
    notes = str(data.get("notes", "")).strip()
    payment = str(data.get("payment", "")).strip()
    transaction_number = str(data.get("transaction_number", "")).strip()

    if not name or not phone or not address:
        return jsonify({"success": False, "message": "يرجى إكمال بيانات العميل"}), 400

    if payment not in ("cash", "shamcash"):
        return jsonify({"success": False, "message": "طريقة الدفع غير صحيحة"}), 400

    if payment == "shamcash" and not transaction_number:
        return jsonify({"success": False, "message": "يرجى إدخال رقم عملية شام كاش"}), 400

    subtotal = cart_total()
    if subtotal <= 0:
        return jsonify({"success": False, "message": "السلة فارغة"}), 400

    delivery_fee = 100
    grand_total = subtotal + delivery_fee

    conn = sqlite3.connect("orders.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders
        (user_id, customer_name, phone, address, notes, payment_method,
         transaction_number, subtotal, delivery_fee, grand_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        name,
        phone,
        address,
        notes,
        payment,
        transaction_number,
        subtotal,
        delivery_fee,
        grand_total
    ))

    order_id = cur.lastrowid

    # حفظ المنتجات الموجودة في السلة داخل الطلب
    for product_id, quantity in get_cart().items():
        product = get_product(int(product_id))

        if not product:
            continue

        item_total = product["price"] * quantity

        cur.execute("""
            INSERT INTO order_items
            (order_id, product_id, product_name, price, quantity, item_total)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            product["id"],
            product["name"],
            product["price"],
            quantity,
            item_total
        ))

    conn.commit()
    conn.close()

    session["cart"] = {}
    session.modified = True

    return jsonify({
        "success": True,
        "order_id": order_id
    })


@app.route("/api/order/<int:order_id>/status")
def order_status(order_id):
    import sqlite3

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "يرجى تسجيل الدخول أولاً"
        }), 401

    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row

    order = conn.execute(
        "SELECT id, status FROM orders WHERE id = ? AND user_id = ?",
        (order_id, user_id)
    ).fetchone()

    conn.close()

    if not order:
        return jsonify({
            "success": False,
            "message": "الطلب غير موجود"
        }), 404

    return jsonify({
        "success": True,
        "order_id": order["id"],
        "status": order["status"] or "جديد"
    })

@app.route("/api/order/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    import sqlite3

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "يرجى تسجيل الدخول أولاً"
        }), 401

    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row

    order = conn.execute(
        "SELECT id, user_id, status FROM orders WHERE id = ? AND user_id = ?",
        (order_id, user_id)
    ).fetchone()

    if not order:
        conn.close()
        return jsonify({
            "success": False,
            "message": "الطلب غير موجود"
        }), 404

    status = order["status"] or "جديد"

    if status != "جديد":
        conn.close()
        return jsonify({
            "success": False,
            "message": "لا يمكن إلغاء الطلب بعد بدء تجهيزه"
        }), 400

    conn.execute(
        "UPDATE orders SET status = ? WHERE id = ? AND user_id = ?",
        ("ملغي", order_id, user_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "تم إلغاء الطلب بنجاح",
        "status": "ملغي"
    })


@app.route("/api/cart")
def cart_api():

    return jsonify({
        "success": True,
        "count": cart_count(),
        "total": cart_total()
    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
