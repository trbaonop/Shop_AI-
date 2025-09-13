const cartList = document.getElementById('cartList');
const totalEl = document.getElementById('total');
const modal = document.getElementById('modal');
const modalBody = document.getElementById('modalBody');
const pendingLabel = document.getElementById('pendingLabel');
const pendingPrice = document.getElementById('pendingPrice');
const pendingQty = document.getElementById('pendingQty');
const btnConfirm = document.getElementById('btnConfirm');

async function refreshCart() {
    try {
        const res = await fetch('/api/cart');
        const data = await res.json();
        renderCart(data);
    } catch (e) {
        console.error('Lỗi khi lấy giỏ hàng:', e);
        cartList.innerHTML = 'Không thể kết nối backend';
    }
}

function renderCart(data) {
    cartList.innerHTML = '';
    if (!data || !data.items || data.items.length === 0) {
        cartList.innerHTML = 'Giỏ trống';
        totalEl.textContent = '0 VND';
        return;
    }
    data.items.forEach(it => {
        const el = document.createElement('div');
        el.className = 'cart-item';
        el.innerHTML = `<div><strong>${it.label}</strong><div style="font-size:12px;color:#6b7280">${it.qty} x ${it.price} VND</div></div>`;
        const rm = document.createElement('div');
        rm.innerHTML = `<button class='btn' onclick="removeFromCart('${it.label}')">-</button> <button class='btn' onclick="addToCart('${it.label}')">+</button>`;
        el.appendChild(rm);
        cartList.appendChild(el);
    });
    totalEl.textContent = (data.total || 0) + ' VND';
}

async function refreshPending() {
    try {
        const res = await fetch('/api/pending');
        const data = await res.json();
        console.log('Dữ liệu từ /api/pending:', data); // Debug
        if (data.label) {
            pendingLabel.textContent = data.label;
            pendingPrice.textContent = `${data.price} VND`;
            pendingQty.textContent = data.qty || 1; // Hiển thị số lượng
            btnConfirm.disabled = false;
        } else {
            pendingLabel.textContent = 'Chưa có';
            pendingPrice.textContent = '0 VND';
            pendingQty.textContent = '0';
            btnConfirm.disabled = true;
        }
    } catch (e) {
        console.error('Lỗi khi lấy pending product:', e);
        pendingLabel.textContent = 'Lỗi kết nối';
        pendingPrice.textContent = '0 VND';
        pendingQty.textContent = '0';
        btnConfirm.disabled = true;
    }
}

async function confirmProduct() {
    try {
        await fetch('/api/confirm', { method: 'POST' });
        await refreshCart();
        await refreshPending();
    } catch (e) {
        console.error('Lỗi khi xác nhận:', e);
    }
}

async function addToCart(label) {
    try {
        await fetch('/api/cart/add', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ label }) });
        await refreshCart();
    } catch (e) {
        console.error('Lỗi khi thêm vào giỏ:', e);
    }
}

async function removeFromCart(label) {
    try {
        await fetch('/api/cart/remove', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ label }) });
        await refreshCart();
    } catch (e) {
        console.error('Lỗi khi xóa khỏi giỏ:', e);
    }
}

async function resetCart() {
    try {
        await fetch('/api/cart/clear', { method: 'POST' });
        await refreshCart();
    } catch (e) {
        console.error('Lỗi khi reset giỏ:', e);
    }
}

async function checkout() {
    try {
        const res = await fetch('/api/checkout', { method: 'POST' });
        const data = await res.json();
        if (data.type === 'qr') {
            modalBody.innerHTML = `<p>Quét mã để thanh toán (amount: ${data.amount} VND)</p><img src="${data.qr_url}" alt="QR" style="width:220px;height:220px">`;
        } else {
            modalBody.innerHTML = data.invoice_html || JSON.stringify(data);
        }
        modal.classList.add('show');
    } catch (e) {
        console.error('Lỗi checkout:', e);
        alert('Lỗi checkout: ' + e.message);
    }
}

function startCamera() {
    console.log('Bật camera');
    // Thêm logic nếu cần
}

function stopCamera() {
    console.log('Tắt camera');
    // Thêm logic nếu cần
}

// === BUTTONS ===
document.getElementById('btnStart').onclick = startCamera;
document.getElementById('btnStop').onclick = stopCamera;
document.getElementById('btnReset').onclick = async () => { await resetCart(); };
document.getElementById('btnCheckout').onclick = checkout;
document.getElementById('btnPrint').onclick = () => { window.print(); };
document.getElementById('modalClose').onclick = () => { modal.classList.remove('show'); };
btnConfirm.onclick = confirmProduct;

setInterval(refreshPending, 800);
setInterval(refreshCart, 1200);

window.addToCart = addToCart;
window.removeFromCart = removeFromCart;