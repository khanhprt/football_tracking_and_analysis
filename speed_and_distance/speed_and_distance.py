import cv2
import sys
sys.path.append("../")
from utils.calculator import *

class  SpeedAndDistance():
    def __init__(self):
        self.frame_rate = 24
        self.frame_window = 5
    
    def add_speed_and_distance_to_tracks(self, tracks):
        total_distance = {}
        for object, object_tracks in tracks.items():
            if object == "ball" or object == "referee":
                continue
            number_of_frames = len(object_tracks)
            for frame_num in range(0, number_of_frames, self.frame_window):
                last_frame = min(frame_num + self.frame_window, number_of_frames - 1)

                for track_id, _ in object_tracks[frame_num].items():
                    if track_id == -1:
                        continue
                    if track_id not in object_tracks[last_frame]:
                        continue
                    start_position = object_tracks[frame_num][track_id]["position_transformed"]
                    end_position = object_tracks[last_frame][track_id]["position_transformed"]

                    if start_position is None or end_position is None:
                        continue

                    distance = measure_distance(start_position, end_position)
                    time_elapsed = (last_frame - frame_num) / self.frame_rate
                    if time_elapsed == 0:
                        time_elapsed = 1
                    speed_meteres_per_second = distance / time_elapsed
                    speed_kilometers_per_hour = speed_meteres_per_second * 3.6
 
                    if object not in total_distance:
                        total_distance[object] = {}
                    
                    if track_id not in total_distance[object]:
                        total_distance[object][track_id] = 0
                    
                    total_distance[object][track_id] += distance

                    for frame_number_bath in range(frame_num, last_frame):
                        if track_id not in object_tracks[frame_number_bath]:
                            continue
                        # Conver cm -> m
                        tracks[object][frame_number_bath][track_id]["speed"] = speed_kilometers_per_hour / 100
                        tracks[object][frame_number_bath][track_id]["distance"] = total_distance[object][track_id] / 100

    def draw_speed_and_distance(self, frames, tracks):
        output_frames = []
        for frame_number, frame in enumerate(frames):
            for object, object_tracks in tracks.items():
                if object == "ball" or object == "referee":
                    continue
                for track_id, track_data in object_tracks[frame_number].items():
                    if track_id == -1:
                        continue
                    if "speed" in track_data:
                        speed = track_data.get("speed", None)
                        distance = track_data.get("distance", None)
                        
                        if speed is None or distance is None:
                            continue

                        bbox = track_data["bbox"]
                        position = get_foot_position(bbox)
                        position = list(position)
                        position[1] += 40

                        position = tuple(map(int, position))
                        cv2.putText(frame, f"{speed:.2f} km/h", position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                        cv2.putText(frame, f"{distance:.2f} m", (position[0], position[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            output_frames.append(frame)
        return output_frames
                            