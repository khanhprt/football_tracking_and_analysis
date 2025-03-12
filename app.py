from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from os import path, makedirs
import jwt  # Thư viện để tạo và xác thực JWT
import datetime 
from functools import wraps
from flask_cors import CORS
import cv2, json
from ultralytics import YOLO
from main import process
from temp.json_export import *

app = Flask(__name__)

CORS(app, origins=["http://localhost:5173"], methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///backend/instance/user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "sdf-1j@#39jksAA11msa:?fdsEo"  # Khóa bí mật để ký JWT
app.config["UPLOAD_FOLDER"] = "backend/uploads"  # Thư mục lưu trữ video tải lên
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # Tăng thời gian timeout

# Tạo thư mục lưu trữ video nếu chưa tồn tại
if not path.exists(app.config["UPLOAD_FOLDER"]):
    makedirs(app.config["UPLOAD_FOLDER"])
    
# Load YOLO model
model = YOLO("yolov8n.pt")  # Sử dụng YOLOv8 nano (có thể thay bằng model khác)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    fullname = db.Column(db.String(80), nullable=False)


with app.app_context():  # Tạo application context
    if not path.exists("user.db"):
        db.create_all()  # Tạo bảng trong cơ sở dữ liệu
        print("Created database!")
        
    # Kiểm tra và thêm user mặc định "test" nếu chưa tồn tại
    test_user = User.query.filter_by(username="test").first()
    if not test_user:
        # Hash mật khẩu "test" trước khi lưu vào cơ sở dữ liệu
        hashed_password = generate_password_hash("test")
        new_user = User(username="test", password=hashed_password, fullname="Trieu Minh Tam")
        db.session.add(new_user)
        db.session.commit()
        print("Created default user: test")
        
        
# Hàm tạo JWT
def create_access_token(user):
    # Thời gian hết hạn của token (ví dụ: 30 phút)
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    # Tạo token với payload chứa user_id và thời gian hết hạn
    token = jwt.encode(
        {"username": user.username, "exp": expiration, "fullname": user.fullname},
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )
    return token      

# Hàm xác thực JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Lấy token từ header Authorization
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]  # Format: Bearer <token>
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # Giải mã token
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.get(data["username"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        # Truyền user hiện tại vào hàm được decorate
        return f(current_user, *args, **kwargs)
    return decorated  

def process_video_with_yolo(video_path):
    # Đọc video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Could not open video file")

    # Lấy thông tin video
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Tạo đường dẫn video đã xử lý
    processed_video_path = path.join(app.config["UPLOAD_FOLDER"], f"processed_{path.basename(video_path)}")
    out = cv2.VideoWriter(processed_video_path, cv2.VideoWriter_fourcc(*"avc1"), fps, (frame_width, frame_height))

    # Xử lý từng frame
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect vật thể bằng YOLO
        results = model(frame)
        annotated_frame = results[0].plot()  # Vẽ bounding box và nhãn lên frame

        # Ghi frame đã xử lý vào video mới
        out.write(annotated_frame)

    # Giải phóng tài nguyên
    cap.release()
    out.release()

    return processed_video_path

def process_ai_football(video_path):
    path, tracks = process(video_path)
    data = clear(tracks)
    return data, path

# Route đăng nhập
@app.route("/api/login", methods=["POST"])
def login():
    # Lấy dữ liệu từ request
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Kiểm tra xem username và password có được cung cấp không
    if not username or not password:
        return jsonify({"message": "Username and password are required!"}), 400

    # Tìm user trong cơ sở dữ liệu
    user = User.query.filter_by(username=username).first()

    # Kiểm tra user và mật khẩu
    if user and check_password_hash(user.password, password):
        # Tạo access_token
        access_token = create_access_token(user)
        return jsonify({
            "message": "Login successful!",
            "token": access_token
        }), 200
    else:
        return jsonify({"message": "Invalid username or password!"}), 401
    
# Route bảo mật (yêu cầu token)
@app.route("/api/upload-video", methods=["POST"])
@token_required
def upload_video():
    # Kiểm tra xem có file video được gửi lên không
    if "video" not in request.files:
        return jsonify({"message": "No video file provided!"}), 400

    video_file = request.files["video"]

    # Kiểm tra xem file có tên không
    if video_file.filename == "":
        return jsonify({"message": "No selected file!"}), 400

    # Lưu video vào thư mục uploads
    video_path = path.join(app.config["UPLOAD_FOLDER"], video_file.filename)
    video_file.save(video_path)
    
    # Xử lý video bằng YOLO
    # processed_video_path = process_video_with_yolo(video_path)
    data, processed_video_path = process_ai_football(video_path)


    return jsonify({
        "message": "Video uploaded successfully!",
        "main_video": processed_video_path[0],
        "circle_video": processed_video_path[1],
        "voronoi_video": processed_video_path[2],
        "line_video": processed_video_path[3],
        "data": data
    }), 200


# Public video
@app.route("/uploads/<filename>")
def serve_video(filename):
    return send_from_directory("uploads", filename, mimetype="video/mp4")

if __name__ == "__main__":
    app.run(debug=True)