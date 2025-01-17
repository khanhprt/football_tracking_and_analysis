import numpy as np
import cv2

from sports.common.view import ViewTransformer
from sports.configs.soccer import SoccerPitchConfiguration

class Transformer:
    def __init__(self):
        # court_w = 64
        # court_h = 35

        self.CONFIG = SoccerPitchConfiguration()

        # self.target = np.array([
        #     [0, 0],
        #     [0, court_w],
        #     [court_h, court_w],
        #     [court_h, 0],
        # ])
        # self.pixel = np.array([
        #     [475, 360],
        #     [7, 928],
        #     [1680, 889],
        #     [1193, 368],
        # ])
        # self.target = self.target.astype(np.float32)
        # self.pixel = self.pixel.astype(np.float32)
        # self.perspective_transform = cv2.getPerspectiveTransform(self.pixel, self.target)

    def transform_matrix(self, keypoints_detection) -> ViewTransformer:
        filter = keypoints_detection.confidence[0] > 0.5
        frame_reference_points = keypoints_detection.xy[0][filter]
        pitch_reference_points = np.array(self.CONFIG.vertices)[filter]
        perspective_transform = ViewTransformer(
            source=frame_reference_points,
            target=pitch_reference_points
        )
        return perspective_transform


    # def transform_point(self, point):
        # p = (int(point[0]), int(point[1]))
        # is_inside = cv2.pointPolygonTest(self.target, p, False)
        # if is_inside >= 0:
        #     return None
        
        # reshaped_point = point.reshape(-1, 1, 2).astype(np.float32)
        # transformed_point = cv2.perspectiveTransform(reshaped_point, self.perspective_transform)
        # transformed_point = transformed_point.reshape(-1, 2)
        # return transformed_point
    
    
    def add_transformed_point(self, tracks):
        for object, object_track in tracks.items():
            for fram_number, track in enumerate(object_track):
                detection_keypoints = track[-1]["pitch"]
                matrix = self.transform_matrix(detection_keypoints)
                for track_id, track_data in track.items():
                    if track_id == -1:
                        continue
                    position = track_data["position_adjusted"]
                    position = np.array(position)
                    # position_transformed = self.transform_point(position)
                    position_transformed = matrix.transform_points(position)
                    if position_transformed is not None:
                        position_transformed = position_transformed.squeeze().tolist()
                    tracks[object][fram_number][track_id]["position_transformed"] = position_transformed