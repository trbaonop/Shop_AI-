import cv2
import torch
import features
import cart
from PIL import Image
import requests

# Các sản phẩm (trùng với tên folder trong samples/)
labels = ["CoCa CoLa", "7 up", "Tương ớt chisu", "nước tương chinsu", "Oreo", "sun cream"]

# Lấy prototype từ features
avg_features, model, preprocess, device = features.get_average_features(labels)

# Ngưỡng unknown
UNKNOWN_THRESHOLD = 0.70  

cap = cv2.VideoCapture(0)
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    image = preprocess(img).unsqueeze(0).to(device)

    with torch.no_grad():
        img_feat = model.encode_image(image)
        img_feat /= img_feat.norm()

    # Tính cosine similarity
    best_label, best_score = None, 0
    for label, proto in avg_features.items():
        sim = torch.cosine_similarity(img_feat, proto, dim=-1).item()
        if sim > best_score:
            best_label, best_score = label, sim

    # Nếu nhận diện hợp lệ → thêm vào giỏ hàng mỗi N frame
    if best_label and best_score >= UNKNOWN_THRESHOLD:
        if frame_count % 30 == 0:  # ~ mỗi giây thêm 1 lần
            cart.add_to_cart(best_label)
            price = cart.PRODUCT_PRICES.get(best_label, 0)  # Lấy giá từ cart
            try:
                requests.post('http://localhost:5000/api/pending', json={'label': best_label, 'price': price})
            except:
                pass
        price = cart.PRODUCT_PRICES.get(best_label, 0)  # Lấy giá từ cart
        display_text = f"{best_label}: {price} VND ({best_score*100:.1f}%)"
    else:
        display_text = f"Unknown ({best_score*100:.1f}%)"

    cv2.putText(frame, display_text, (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    # Vẽ giỏ hàng
    cart.draw_cart(frame)

    cv2.imshow("CLIP Product Recognition + Cart", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # thoát
        break
    elif key == ord('r'):  # reset giỏ hàng
        cart.clear_cart()
    elif key == ord('d'):  # demo xóa 1 sản phẩm (vd Oreo)
        cart.remove_from_cart("Oreo")

cap.release()
cv2.destroyAllWindows()