# features.py
import os
import torch
import clip
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
# Load CLIP model (RN50 nhẹ, ViT-B/32 chính xác hơn)
model, preprocess = clip.load("RN50", device=device)

def get_average_features(labels, samples_dir="D:\code\shimeji-main\AI_Project\dataset\samples"):
    avg_features = {}
    with torch.no_grad():
        for label in labels:
            folder = os.path.join(samples_dir, label)
            if not os.path.exists(folder):
                print(f"[WARN] Chưa có thư mục {folder}, bỏ qua")
                continue

            embeddings = []
            for fname in os.listdir(folder):
                if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    img_path = os.path.join(folder, fname)
                    img = preprocess(Image.open(img_path)).unsqueeze(0).to(device)
                    feat = model.encode_image(img)
                    feat /= feat.norm()
                    embeddings.append(feat)

            if embeddings:
                embeddings = torch.stack(embeddings).mean(dim=0)
                embeddings /= embeddings.norm()
                avg_features[label] = embeddings
                print(f"[INFO] Prototype {label} đã tạo")
            else:
                print(f"[WARN] Không có ảnh trong {folder}")

    return avg_features, model, preprocess, device
