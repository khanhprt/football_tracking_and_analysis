from ultralytics import YOLO
import supervision as sv
import torch
import pandas as pd
import cv2
import numpy as np
import supervision as sv
from utils.calculator import *

class Tracker:
    def __init__(self, model_path, model_keypoints_path):
        self.model = YOLO(model_path)
        self.model_keypoints = YOLO(model_keypoints_path)
        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.2,
            lost_track_buffer=50,
            minimum_matching_threshold=0.7,
            frame_rate=50,
            minimum_consecutive_frames=2
        )

    def detect_frames(self, frames):
        detections = []
        detections_keypoints = []
        batch = 20

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device=device)
        for i in range(0, len(frames), batch):
        # for i in range(0, 60, batch):
            detection_batch = self.model.predict(frames[i:i+batch], conf=0.2, save=False)
            detection_keypoints_batch = self.model_keypoints.predict(
                                        frames[i:i+batch], conf=0.3, save=False)
            detections += detection_batch
            detections_keypoints += detection_keypoints_batch
        return detections, detections_keypoints
    
    def get_object_tracks(self, frames):

        detections, detections_keypoints = self.detect_frames(frames)

        tracks = {
            "players": [],
            "referees": [],
            "ball": [],
            # "goalkeeper": []
        }
        
        for frame_number, (detection, detection_keypoints) in enumerate(zip(detections, detections_keypoints)):
            cls_name = detection.names

            detection_sv = sv.Detections.from_ultralytics(detection)
            detection_keypoints_sv = sv.KeyPoints.from_ultralytics(detection_keypoints)
            cls_name_invert = { v:k for k, v in cls_name.items() }

            # Truyen frame de tracking
            detection_tracks = self.tracker.update_with_detections(detection_sv)

            tracks["ball"].append({})
            tracks["players"].append({})
            tracks["referees"].append({})

           # Update tracking
            tracks["ball"][frame_number][-1] = {"pitch":detection_keypoints_sv}
            tracks["players"][frame_number][-1] = {"pitch":detection_keypoints_sv}
            tracks["referees"][frame_number][-1] = {"pitch":detection_keypoints_sv}

            for frame_detection in detection_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_name_invert["player"]:
                    tracks["players"][frame_number][track_id] = {"bbox":bbox} 

                if cls_id == cls_name_invert["referee"]:
                    tracks["referees"][frame_number][track_id] = {"bbox":bbox} 
            
            for frame_detect in detection_sv:
                bbox = frame_detect[0].tolist()
                cls_id = frame_detect[3]

                if cls_id == cls_name_invert["ball"]:
                    tracks["ball"][frame_number][1] = {"bbox":bbox}
        
        return tracks

    def add_position_to_tracks(self, tracks):
        for object, object_tracks in tracks.items():
            for frame_number, track in enumerate(object_tracks):
                for track_id, track_data in track.items():
                    if track_id == -1:
                        continue
                    bbox = track_data["bbox"]
                    if object == "ball":
                        track_data["position"] = get_center_of_bbox(bbox)
                    else:
                        track_data["position"] = get_foot_position(bbox)
    
    def interpolate_ball_position(self, ball_position):
        ball_position = [x.get(1, {}).get("bbox", []) for x in ball_position]
        df_ball_position = pd.DataFrame(ball_position, columns=["x1", "y2", "x2", "y2"])

        df_ball_position = df_ball_position.interpolate()
        df_ball_position = df_ball_position.bfill()

        ball_position = [{1: {"bbox": x}} for x in df_ball_position.to_numpy().tolist()]

        return ball_position
    
    def draw_annotation(self, frames, tracks, team_ball_control):
        output_video_frames = []

        for frame_number, frame in enumerate(frames):
            frame = frame.copy()

            player_dict = tracks["players"][frame_number]
            ball_dict = tracks["ball"][frame_number]
            referee_dict = tracks["referees"][frame_number]

            # Draw players
            for track_id, player in player_dict.items():
                if track_id == -1:
                    continue
                color = player.get("team_color", (0, 0, 255))
                frame = self.draw_ellipse(frame, player["bbox"], color, track_id)

                if player.get("has_control", False):
                    frame = self.draw_traingle(frame, player["bbox"], (0, 0, 255))
            
            # Draw Referees
            for track_id, referee in referee_dict.items():
                if track_id == -1:
                    continue
                frame = self.draw_ellipse(frame, referee["bbox"], (0, 255, 255))
            
            # Draw Ball
            for track_id, ball in ball_dict.items():
                if track_id == -1:
                    continue
                frame = self.draw_traingle(frame, ball["bbox"], (0, 255, 0))
            
            frame = self.draw_team_ball_control(frame, frame_number, team_ball_control)

            output_video_frames.append(frame)
        return output_video_frames
    
    def draw_team_ball_control(self, frame, frame_number, team_ball_control):
        overlap = frame.copy()

        cv2.rectangle(overlap, (1350, 850), (1900, 970), (255, 255, 255), -1)
        alpha = 0.4
        cv2.addWeighted(overlap, alpha, frame, 1 - alpha, 0, frame)
        team_ball_control_till_frame = team_ball_control[:frame_number+1]

        team_1_number_frames = team_ball_control_till_frame[team_ball_control_till_frame == 1].shape[0]
        team_2_number_frames = team_ball_control_till_frame[team_ball_control_till_frame == 2].shape[0]

        team_1 = team_1_number_frames / (team_1_number_frames + team_2_number_frames)
        team_2 = team_2_number_frames / (team_1_number_frames + team_2_number_frames)

        cv2.putText(frame, f"Team 1: {team_1*100:.2f}%", (1400, 900), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(frame, f"Team 2: {team_2*100:.2f}%", (1400, 950), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        return frame

    def draw_ellipse(self, frame, bbox, color, track_id=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)

        cv2.ellipse(frame,
                    center=(x_center, y2),
                    axes=(int(width), int(0.35*width)),
                    angle=0,
                    startAngle=-45,
                    endAngle=235,
                    color = color,
                    thickness=2,
                    lineType=cv2.LINE_4)
        
        rectangle_width = 40
        rectangle_height = 20
        x1_rect = int(x_center - rectangle_width // 2)
        x2_rect = int(x_center + rectangle_width // 2)
        y1_rect = int((y2 - rectangle_height//2) + 15)
        y2_rect = int((y2 + rectangle_height//2) + 15)

        if track_id is not None:
            cv2.rectangle(frame, (x1_rect, y1_rect), (x2_rect, y2_rect), color, cv2.FILLED)

            x1_text = int(x1_rect + 12)
            y1_text = int(y1_rect + 15)
            
            cv2.putText(frame, 
                        f"{track_id}",
                        (x1_text, y1_text),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.6,
                        (0, 0, 0),
                        2)
        return frame
    
    def draw_traingle(self, frame, bbox, color):
        y = int(bbox[1])
        x, _ = get_center_of_bbox(bbox)

        triangle = np.array([
            [x, y],
            [x-10, y-20],
            [x+10, y-20]
        ])
        cv2.drawContours(frame, [triangle], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [triangle], 0, (0, 0, 0), 2)

        return frame
    
    def release(self):
        del self.model
        del self.model_keypoints
        del self.tracker
