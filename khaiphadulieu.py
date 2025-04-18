# -*- coding: utf-8 -*-
"""KhaiPhaF (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KmRYgJAz0ynsDnop30V7CWdpZGladO3B
"""

from google.colab import drive
import os
import pandas as pd

try:
    from ultralytics import YOLO
except ModuleNotFoundError:
    !pip install ultralytics
    from ultralytics import YOLO

drive.mount('/content/drive')

base_dir = "/content/drive/MyDrive/dataset_hoa"
images_dir = os.path.join(base_dir, "images")
labels_dir = os.path.join(base_dir, "labels")
yaml_path = os.path.join(base_dir, "data.yaml")

os.makedirs(images_dir, exist_ok=True)
os.makedirs(labels_dir, exist_ok=True)
print("✅ Đã tạo thư mục images và labels!")

import os

class_file = os.path.join(labels_dir, "classes.txt")

if os.path.exists(class_file):
    with open(class_file, "r") as f:
        class_list = [line.strip() for line in f.readlines()]
else:
    print(f"File {class_file} không tồn tại.")

def process_labels():
    for file in os.listdir(labels_dir):
        if file.endswith(".txt") and file != "classes.txt":
            lines = []
            with open(os.path.join(labels_dir, file), "r") as f:
                for line in f.readlines():
                    values = line.strip().split()
                    if len(values) < 5:
                        continue  # Bỏ qua dòng lỗi
                    class_id = int(values[0])

                    # Chỉnh sửa class_id nếu >= 20
                    if class_id >= 20:
                        print(f"⚠ Chỉnh sửa {file}: class_id {class_id} -> 0")
                        class_id = 0

                    lines.append(f"{class_id} " + " ".join(values[1:]) + "\n")

            # Ghi đè file với dữ liệu đã chỉnh sửa
            with open(os.path.join(labels_dir, file), "w") as f:
                f.writelines(lines)

process_labels()
print("✅ Đã sửa xong tất cả file nhãn!")

data = []
for label_file in os.listdir(labels_dir):
    if label_file.endswith(".txt") and label_file != "classes.txt":
        img_file = label_file.replace(".txt", ".jpg")  # Đổi thành .png nếu dùng PNG
        with open(os.path.join(labels_dir, label_file), "r") as f:
            for line in f:
                values = line.strip().split()
                if len(values) < 5:
                    continue
                class_id = int(values[0])
                x_center, y_center, width, height = map(float, values[1:])
                if class_id < len(class_list):
                    data.append([img_file, x_center, y_center, width, height, class_list[class_id]])

df = pd.DataFrame(data, columns=["filename", "x_center", "y_center", "width", "height", "class"])
csv_path = os.path.join(base_dir, "labels.csv")
df.to_csv(csv_path, index=False)
print(f"✅ Đã lưu CSV: {csv_path}")

yaml_content = f"""path: {base_dir}
train: images
val: images
test: images
names:
""" + "\n".join([f"  {i}: {class_name}" for i, class_name in enumerate(class_list)])

with open(yaml_path, "w") as file:
    file.write(yaml_content)

print("✅ Đã tạo file data.yaml thành công!")

from ultralytics import YOLO

# Load mô hình YOLOv8n (nhẹ nhất)
model = YOLO("yolov8s.pt")

# Huấn luyện mô hình
model.train(
    data="/content/drive/MyDrive/dataset_hoa/data.yaml",  # Đường dẫn đến data.yaml
    epochs=200,       # Số vòng huấn luyện
    imgsz=640,       # Kích thước ảnh
    batch=8,         # Số batch
    device=0,        # Sử dụng GPU nếu có
    project="/content/drive/MyDrive/dataset_hoa/my_model",  # Lưu kết quả vào thư mục này
    name="custom_train"  # Tên thư mục con
)

from ultralytics import YOLO

model = YOLO("runs/detect/train/weights/best.pt")  # Load mô hình tốt nhất
results = model("/content/drive/MyDrive/dataset_hoa/images/z6456883842281_a0afa4759cc5447d71951aaf6242bb1f.jpg", save=True)  # Test trên ảnh mới

from ultralytics import YOLO
import cv2
import numpy as np
from google.colab.patches import cv2_imshow
from google.colab import files

# Chọn file từ máy tính
uploaded = files.upload()  # Mở hộp thoại để chọn file

# Lấy tên file đã upload
image_path = list(uploaded.keys())[0]

# Load mô hình đã huấn luyện
model_path = "/content/drive/MyDrive/dataset_hoa/my_model/custom_train5/weights/best.pt"
model = YOLO(model_path)

# Đọc ảnh từ file đã chọn
image = cv2.imread(image_path)

# Nhận diện đối tượng
results = model.predict(image, conf=0.6)

# Lặp qua từng kết quả và vẽ khung bao quanh đối tượng
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = result.names[int(box.cls[0])]
        confidence = box.conf[0]

        # Vẽ bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Hiển thị tên và độ tin cậy trên ảnh
        text = f"{label}: {confidence:.2f}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        text_x, text_y = x1, y1 - 10

        # Vẽ nền chữ
        cv2.rectangle(image, (text_x, text_y - text_size[1] - 5),
                      (text_x + text_size[0], text_y + 5), (0, 255, 0), -1)

        # Hiển thị chữ trên nền
        cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 0), 2)

# Hiển thị ảnh kết quả
cv2_imshow(image)
cv2.waitKey(0)
cv2.destroyAllWindows()

from ultralytics import YOLO
import cv2
import numpy as np
from google.colab.patches import cv2_imshow
from google.colab import files
import os

# Chọn nhiều ảnh từ máy
uploaded = files.upload()

# Load mô hình đã huấn luyện
model_path = "/content/drive/MyDrive/dataset_hoa/my_model/custom_train5/weights/best.pt"
model = YOLO(model_path)

# Tạo thư mục lưu kết quả
os.makedirs("predicted_results", exist_ok=True)

# Nếu bạn đã gán label tiếng Việt trong data.yaml thì YOLO sẽ tự dùng luôn
custom_labels = {
    15: 'Hoa Hai Duong',
    16: 'hoa Hong Do',
    17: 'Hoa Hong Phan',
    18: 'Hoa Huong Duong',
    19: 'Hoa Hong Nhat'
}

# Duyệt qua từng ảnh
for image_name in uploaded.keys():
    image = cv2.imread(image_name)
    results = model.predict(image, conf=0.6)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            confidence = float(box.conf[0])

            label = custom_labels.get(cls_id, f"Class {cls_id}")
            text = f"{label} ({confidence:.2f})"

            # Font size nhỏ lại, phù hợp box
            font_scale = 0.4
            font_thickness = 1
            color = (0, 255, 0)

            # Vẽ box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 1)

            # Tính kích thước nhãn
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
            text_w, text_h = text_size

            # Vị trí nhãn không đè đối tượng
            text_x = x1
            text_y = y1 - 10 if y1 - 10 > 10 else y1 + 10

            # Nền cho nhãn
            cv2.rectangle(image, (text_x, text_y - text_h - 4),
                          (text_x + text_w + 4, text_y), color, -1)

            # Ghi nhãn
            cv2.putText(image, text, (text_x + 2, text_y - 2),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness)

    # Hiển thị ảnh
    print(f"Kết quả cho ảnh: {image_name}")
    cv2_imshow(image)

    # Lưu ảnh kết quả
    result_path = f"predicted_results/result_{image_name}"
    cv2.imwrite(result_path, image)

# Tạo link tải ảnh về
#!zip -r predicted_results.zip predicted_results
#files.download("predicted_results.zip")

!pip install -q gradio
import gradio as gr

import os

model_path = "/content/drive/MyDrive/dataset_hoa/my_model/custom_train4/weights/best.pt"

if os.path.exists(model_path):
    print("File tồn tại.")
else:
    print("File không tồn tại. Kiểm tra lại đường dẫn.")