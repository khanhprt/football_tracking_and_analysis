import cv2
import supervision as sv
import pickle
import numpy as np

from temp.process_frame import *
from sports.configs.soccer import SoccerPitchConfiguration
from sports.annotators.soccer import (
    draw_pitch,
    draw_points_on_pitch,
    draw_pitch_voronoi_diagram
)

CONFIG = SoccerPitchConfiguration()

def add_pitch_image(origin: np.ndarray, pitch_frame: np.ndarray):
    o_h, o_w = origin.shape[:2]
    p_h, p_w = pitch_frame.shape[:2]

    x_position = (o_w - p_w) //2
    y_position = (o_h - p_h)
    overlay = origin[y_position:y_position + p_h, x_position:x_position + p_w]

    # Tạo mask cho màu mà bạn muốn giữ nguyên
    mask = np.all(overlay == (86, 196, 86), axis=-1)
    overlay[mask] = origin[y_position:y_position + p_h, x_position:x_position + p_w][mask]

    # Kết hợp ảnh nhỏ với ảnh lớn, với độ mờ:
    alpha_small = 0.5  # Độ mờ của ảnh nhỏ (0 là hoàn toàn trong suốt, 1 là hoàn toàn không trong suốt)
    alpha_large = 1 - alpha_small  # Độ mờ của ảnh lớn

    blended = cv2.addWeighted(overlay, alpha_large, pitch_frame, alpha_small, 0)


    origin[y_position:y_position + p_h, x_position:x_position + p_w] = blended

    return origin




# frames = read_video("inputs/ok_798b45_0.mp4")
frames = read_video("outputs/ok_798b45_0.avi")
# print(frames[0].shape)

pitch_frame = draw_pitch(CONFIG)
# cv2.imshow("Pitch Frame", pitch_frame)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Đường dẫn tới file .pkl
file_path = "outputs/tracks.pkl"

# Mở và tải dữ liệu từ file .pkl
with open(file_path, 'rb') as file:
    tracks = pickle.load(file)

output_frames = []
team1_xy = []
team2_xy = []
team1_color = None
team2_color = None
# Hiển thị dữ liệu đã tải
for object, object_track in tracks.items():
    if object != "players":
        continue
    for frame_number, track in enumerate(object_track):
        pitch_frame = draw_pitch(CONFIG)
        for track_id, track_data in track.items():
            if track_id == -1:
                continue
            point = track_data["position_transformed"]
            color = track_data["team_color"]
            # cv2.circle(pitch_frame, (int(point[0]/10), int(point[1]/10)), 20, color, -1)
            if track_data["team"] == 1:
                team1_xy.append((int(point[0]/10), int(point[1]/10)))
                team1_color = sv.Color.from_rgb_tuple(color)
            elif track_data["team"] == 2:
                team2_xy.append((int(point[0]/10), int(point[1]/10)))
                team2_color = sv.Color.from_rgb_tuple(color)


        # print(pitch_frame.shape)
        new_width = int(pitch_frame.shape[1] // 2)
        new_height = int(pitch_frame.shape[0] // 2)
        new_size = (new_width, new_height)


        # Resize ảnh
        # resized_image = cv2.resize(pitch_frame, new_size, interpolation=cv2.INTER_AREA)
        # image = add_pitch_image(frames[frame_number], resized_image)
        # output_frames.append(image)

        # cv2.imshow("Pitch Frame", image)
        # cv2.waitKey(10)
        voronoi_image = draw_pitch_voronoi_diagram(
            CONFIG,
            team_1_xy=np.array(team1_xy),
            team_2_xy=np.array(team2_xy),
            team_1_color=team1_color,
            team_2_color=team2_color,
            pitch=pitch_frame
        )
        cv2.imshow("Voronoi Diagram", voronoi_image)
        cv2.waitKey(0)



# write_video("add.avi", output_frames)