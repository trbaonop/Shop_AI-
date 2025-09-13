
import cv2

# Bảng giá sản phẩm (demo)
PRODUCT_PRICES = {
    "CoCa CoLa": 12000,
    "7 up": 11000,
    "Tương ớt chisu": 15000,
    "nước tương chinsu": 13000,
    "Oreo": 10000,
    "sun cream": 20000
}

cart = {}  # giỏ hàng: {"Tên": {"qty": x, "price": y}}

def add_to_cart(label):
    if label not in PRODUCT_PRICES:
        return
    if label in cart:
        cart[label]["qty"] += 1
    else:
        cart[label] = {"qty": 1, "price": PRODUCT_PRICES[label]}

def remove_from_cart(label):
    if label in cart:
        cart[label]["qty"] -= 1
        if cart[label]["qty"] <= 0:
            del cart[label]

def clear_cart():
    cart.clear()

def get_cart_total():
    return sum(item["qty"] * item["price"] for item in cart.values())

def draw_cart(frame):
    x, y = 20, 80
    cv2.putText(frame, "=== Gio hang ===", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    y += 30
    for label, item in cart.items():
        line = f"{label}: {item['qty']} x {item['price']} = {item['qty']*item['price']}"
        cv2.putText(frame, line, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
        y += 25
    cv2.putText(frame, f"Tong tien: {get_cart_total()} VND", (x, y+10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
