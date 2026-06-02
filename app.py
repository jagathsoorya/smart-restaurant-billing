from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "restaurant_secret_key"

ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "123"

menu = {
    "Pizza": 120,
    "Burger": 80,
    "Salad": 40,
    "Coffee": 25,
    "Pasta": 100,
    "Sandwich": 60,
    "Fries": 50,
    "Momos": 90,
    "Icecream": 70,
    "Fried Rice": 110,
    "Noodles": 95,
    "Chicken Roll": 85,
    "Milkshake": 75
}

coupons = {
    "JAGATH20": 0.20,
    "SAVE10": 0.10
}

order_history = []
transaction_history = []


@app.route("/", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/home")
def home():
    if "admin" not in session:
        return redirect(url_for("login"))

    return render_template("index.html", menu=menu)


@app.route("/generate_bill", methods=["POST"])
def generate_bill():
    if "admin" not in session:
        return redirect(url_for("login"))

    customer_name = request.form.get("customer_name", "").strip()
    customer_phone = request.form.get("customer_phone", "").strip()
    table_no = request.form.get("table_no", "").strip()
    order_type = request.form.get("order_type", "")
    payment_method = request.form.get("payment_method", "")
    coupon = request.form.get("coupon", "").upper().strip()

    # Basic validation
    if not customer_name.replace(" ", "").isalpha():
        return "Error: Customer name should contain only alphabets."

    if not customer_phone.isdigit():
        return "Error: Mobile number should contain only numbers."

    if not table_no.isdigit():
        return "Error: Table number should contain only numbers."

    ordered_items = []
    total_bill = 0
    total_items = 0

    # Corrected menu loop
    for item, price in menu.items():
        qty_value = request.form.get(item, "0")

        if qty_value == "":
            qty = 0
        else:
            qty = int(qty_value)

        if qty > 0:
            item_total = price * qty
            ordered_items.append((item, qty, item_total))
            total_bill += item_total
            total_items += qty

    discount = 0

    if coupon in coupons:
        discount = total_bill * coupons[coupon]

    final_bill = total_bill - discount
    gst = final_bill * 0.05
    grand_total = final_bill + gst

    bill_no = random.randint(1000, 9999)
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    filename = f"Bill_{bill_no}.txt"

    with open(filename, "w") as file:
        file.write("FOODIES HUB BILL\n")
        file.write(f"Bill No: {bill_no}\n")
        file.write(f"Customer Name: {customer_name}\n")
        file.write(f"Mobile: {customer_phone}\n")
        file.write(f"Table No: {table_no}\n")
        file.write(f"Order Type: {order_type}\n")
        file.write(f"Date & Time: {current_time}\n\n")

        file.write("Items Ordered:\n")
        for item, qty, price in ordered_items:
            file.write(f"{item} x {qty} = Rs.{price}\n")

        file.write(f"\nSubtotal: Rs.{total_bill:.2f}\n")
        file.write(f"Discount: Rs.{discount:.2f}\n")
        file.write(f"GST: Rs.{gst:.2f}\n")
        file.write(f"Grand Total: Rs.{grand_total:.2f}\n")
        file.write(f"Payment Method: {payment_method}\n")

    order_record = {
        "bill_no": bill_no,
        "customer_name": customer_name,
        "phone": customer_phone,
        "table_no": table_no,
        "order_type": order_type,
        "total_items": total_items,
        "grand_total": grand_total,
        "date_time": current_time
    }

    transaction_record = {
        "bill_no": bill_no,
        "payment_method": payment_method,
        "amount": grand_total,
        "date_time": current_time
    }

    order_history.append(order_record)
    transaction_history.append(transaction_record)

    return render_template(
        "bill.html",
        bill_no=bill_no,
        customer_name=customer_name,
        customer_phone=customer_phone,
        table_no=table_no,
        order_type=order_type,
        payment_method=payment_method,
        ordered_items=ordered_items,
        total_bill=total_bill,
        discount=discount,
        gst=gst,
        grand_total=grand_total,
        total_items=total_items,
        current_time=current_time,
        filename=filename
    )


@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))

    total_orders = len(order_history)
    total_revenue = sum(order["grand_total"] for order in order_history)
    total_transactions = len(transaction_history)

    return render_template(
        "dashboard.html",
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_transactions=total_transactions
    )


@app.route("/orders")
def orders():
    if "admin" not in session:
        return redirect(url_for("login"))

    return render_template("orders.html", orders=order_history)


@app.route("/transactions")
def transactions():
    if "admin" not in session:
        return redirect(url_for("login"))

    return render_template("transactions.html", transactions=transaction_history)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)