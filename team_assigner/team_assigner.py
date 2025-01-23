from sklearn.cluster import KMeans
from sports.common.team import TeamClassifier
import numpy as np
import gc
from utils import *

class TeamAssigner:
    def __init__(self):
        self.team_color = {}
        self.player_team_dict = {}
        self.team_classifier = TeamClassifier(device="cuda")
        self._iscompleted = {1: False, 2: False}

    def assign_team_color(self, image_crop, team):

        color = self.get_player_color(image_crop)
        self.team_color[team] = color
        if team == 1:
            self._iscompleted[1] = True
        elif team == 2:
            self._iscompleted[2] = True

    def assign_team_classifier(self, frames, tracks):
        # player_colors = []
        crops = []

        # for id, player_detection in player_detection.items():
        #     if id == -1:
        #         continue

        #     bbox = player_detection["bbox"]
        #     player_color, player_crop = self.get_player_color(frame, bbox)
        #     player_colors.append(player_color)
            # player_crops.append(player_crop)
            # crops += player_crop
        
        for object, object_track in tracks.items():
            if object != "players":
                continue
            for frame_number, track in enumerate(object_track):
                try:
                    player_crops = []
                    for track_id, track_data in track.items():
                        if track_id == -1:
                            continue
                        bbox = track_data["bbox"]
                        image = frames[frame_number][int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
                        player_crops.append(image)
                    crops += player_crops
                    player_crops.clear()
                except Exception as e:
                    print(frame_number)
                    print(e)
                    return
                    
        # kmeans = KMeans(n_clusters=2, init='k-means++', n_init=10)
        # kmeans.fit(player_colors)

        self.team_classifier.fit(crops)
        # self.kmeans = kmeans
        # self.team_color[1] = kmeans.cluster_centers_[0]
        # self.team_color[2] = kmeans.cluster_centers_[1]
    
    def get_player_color(self, image):
        # image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]

        top_half_image = image[0:int(image.shape[0]/2), :]

        kmeans = self.get_clustering_model(top_half_image)

        labels = kmeans.labels_

        clustered_image = labels.reshape(top_half_image.shape[0],top_half_image.shape[1])

        corner_clusters = [clustered_image[0,0],clustered_image[0,-1],clustered_image[-1,0],clustered_image[-1,-1]]
        non_player_cluster = max(set(corner_clusters),key=corner_clusters.count)
        player_cluster = 1 - non_player_cluster

        player_color = kmeans.cluster_centers_[player_cluster]

        return player_color
    
    def get_clustering_model(self, image):
        
        image_2d = image.reshape(-1, 3)
        kmeans = KMeans(n_clusters=2, init='k-means++', n_init=1)
        kmeans = kmeans.fit(image_2d)

        return kmeans
    
    def get_player_team(self, frame, player_bbox, player_id):
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]
        
        player_color, player_crop = self.get_player_color(frame, player_bbox)

        reshape_player_color = player_color.reshape(1, -1)
        # team_id = self.kmeans.predict(reshape_player_color)[0] + 1
        team_id = self.team_classifier.predict(player_crop)

        self.player_team_dict[player_id] = team_id
        
        return team_id

    def get_player_crops(self, frame, player_track, frame_number, tracks):
        crops = []
        id_in_frame = []
        for player_id, track in player_track.items():
            if player_id == -1:
                continue
            bbox = track['bbox']
            player_crop = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
            crops.append(player_crop)
            id_in_frame.append(player_id)

        detect_team_id = self.team_classifier.predict(crops)
        detect_team_id = detect_team_id.astype(int)

        for i in range(len(id_in_frame)):
            player_id = id_in_frame[i]
            team = detect_team_id[i] + 1
            if not self._iscompleted[team]:
                self.assign_team_color(crops[i], team)

            # if player_id in self.player_team_dict:
            #     history_team = self.player_team_dict[player_id]
            #     # Nếu muốn giảm check team
            #     tracks["players"][frame_number][player_id]["team"] = history_team
            #     tracks["players"][frame_number][player_id]["team_color"] = self.team_color[history_team]
            #     # Check full frame
            #     # tracks["players"][frame_number][player_id]["team"] = team
            #     # tracks["players"][frame_number][player_id]["team_color"] = self.team_color[team]
            #     # self.player_team_dict[player_id] = team
            # else:
            #     tracks["players"][frame_number][player_id]["team"] = team
            #     tracks["players"][frame_number][player_id]["team_color"] = self.team_color[team]
            #     self.player_team_dict[player_id] = team
            tracks["players"][frame_number][player_id]["team"] = team
            tracks["players"][frame_number][player_id]["team_color"] = self.team_color[team]
    
    def resolve_goalkeepers(self, tracks):
        # Resolve goalkeeper positions based on the detected teams
        for object, object_tracks in tracks.items():
            for frame_number, track in enumerate(object_tracks):
                team1_postions = []
                team2_postions = []
                team_color_1 = None
                team_color_2 = None

                if object == "players":
                    for track_id, track_data in track.items():
                        if track_id == -1 or track_id == -2:
                            continue
                        if track_data["team"] == 1:
                            team1_postions.append(track_data["position"])
                            team_color_1 = track_data["team_color"]
                        elif track_data["team"] == 2:
                            team2_postions.append(track_data["position"])
                            team_color_2 = track_data["team_color"]

                team1_mean = np.mean(np.array(team1_postions), axis=0)
                team2_mean = np.mean(np.array(team2_postions), axis=0)
                if object == "goalkeepers":
                    for track_id, track_data in track.items():
                        if track_id == -1 or track_id == -2:
                            continue
                        goalkeeper_position = track_data["position"]
                        dist_1 = np.linalg.norm(goalkeeper_position - team1_mean)
                        dist_2 = np.linalg.norm(goalkeeper_position - team2_mean)
                        if dist_1 < dist_2:
                            track_data["team"] = 1
                            track_data["team_color"] = team_color_1
                        elif dist_2 < dist_1:
                            track_data["team"] = 2
                            track_data["team_color"] = team_color_2

    def release(self):
        del self.team_classifier
        del self.player_team_dict
        del self.team_color
        gc.collect()
