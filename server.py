from flask import Flask, jsonify, request, render_template
from threading import Lock
import cart

app = Flask(__name__, static_folder="static", template_folder="templates")
detections = []
pending_product = None  # Lưu sản phẩm đang nhận diện: {label, price, qty}
det_lock = Lock()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/detections', methods=['GET', 'POST'])
def api_detections():
    global detections
    if request.method == 'GET':
        with det_lock:
            return jsonify(detections)
    else:
        data = request.get_json()
        with det_lock:
            detections = data
        return ('', 204)

@app.route('/api/pending', methods=['GET', 'POST'])
def api_pending():
    global pending_product
    if request.method == 'GET':
        return jsonify(pending_product or {})
    else:
        data = request.get_json()
        with det_lock:
            if pending_product and pending_product.get('label') == data.get('label'):
                pending_product['qty'] = pending_product.get('qty', 1) + 1  # Tăng số lượng
            else:
                pending_product = {'label': data.get('label'), 'price': data.get('price'), 'qty': 1}  # Tạo mới
        return ('', 204)

@app.route('/api/confirm', methods=['POST'])
def api_confirm():
    global pending_product
    if pending_product and pending_product.get('label'):
        for _ in range(pending_product.get('qty', 1)):  # Thêm số lượng tương ứng
            cart.add_to_cart(pending_product['label'])
        pending_product = None  # Xóa sau khi xác nhận
    return ('', 204)

@app.route('/api/cart', methods=['GET'])
def api_cart():
    items = [{'label': label, 'qty': info['qty'], 'price': info['price']} for label, info in cart.cart.items()]
    return jsonify({'items': items, 'total': cart.get_cart_total()})

@app.route('/api/cart/add', methods=['POST'])
def api_add():
    data = request.get_json()
    cart.add_to_cart(data.get('label'))
    return ('', 204)

@app.route('/api/cart/remove', methods=['POST'])
def api_remove():
    data = request.get_json()
    cart.remove_from_cart(data.get('label'))
    return ('', 204)

@app.route('/api/cart/clear', methods=['POST'])
def api_clear():
    cart.clear_cart()
    return ('', 204)

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    total = cart.get_cart_total()
    qr_url = f"https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl=PAY%3A{total}"
    invoice_html = f"<h3>Hóa đơn</h3><p>Tổng: {total} VND</p>"
    cart.clear_cart()
    return jsonify({'type': 'qr', 'qr_url': qr_url, 'amount': total, 'invoice_html': invoice_html})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)