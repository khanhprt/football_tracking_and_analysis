from flask import jsonify
import pickle
import json
import numpy as np


def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {convert_numpy(k): convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy(x) for x in obj]
    return obj

def clear(tracks:dict):
    for object, object_track in tracks.items():
        for fram_number, track in enumerate(object_track):
            if -1 in track:
                del track[-1]
            for track_id, track_data in track.items():
                if object != "players":
                    continue
                color = track_data["team_color"]
                tracks[object][fram_number][track_id]["team_color"] = color.tolist()
    return tracks

file_path = "outputs/tracks.pkl"

# Mở và tải dữ liệu từ file .pkl
with open(file_path, 'rb') as file:
    tracks = pickle.load(file)

tracks = clear(tracks)

tracks = convert_numpy(tracks)

json_string = json.dumps(tracks, indent=4)  # indent=4 để dễ đọc
print(jsonify(tracks))

