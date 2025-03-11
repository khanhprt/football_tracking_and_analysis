from temp.process_frame import *
from tracking.tracking import *
from camera_movement.camera_movement import *
from transformer.transformer import *
from speed_and_distance.speed_and_distance import *
from team_assigner.team_assigner import *
from player_ball_assigner.player_ball_assigner import *
import os
import pickle


def process(video_path, model_path="models/yolov8x-football.pt", 
            model_keypoints_path="models/key_points_pitch_ver2.pt",
            load_pkl=True):

    frames = read_video(video_path)

    tracker = Tracker(model_path, model_keypoints_path)
    camera_movement = CameraMovement(frames[0])
    speed_and_distance = SpeedAndDistance()

    if load_pkl:
        with open("./outputs/tracks.pkl", "rb") as f:
            tracks = pickle.load(f)
    else:
        tracks = tracker.get_object_tracks(frames)
        tracker.add_position_to_tracks(tracks)

    if load_pkl:
        with open("./outputs/camera_movement_frames.pkl", "rb") as f:
            camera_movement_frames = pickle.load(f)
    else:   
        camera_movement_frames = camera_movement.get_camera_movement(frames)
        camera_movement.add_camera_movement_to_tracks(tracks, camera_movement_frames)

    if not load_pkl:
        transformer = Transformer()
        transformer.add_transformed_point(tracks)

        tracks["ball"] = tracker.interpolate_ball_position(tracks["ball"])

        speed_and_distance.add_speed_and_distance_to_tracks(tracks)

        team_assigner = TeamAssigner()
        team_assigner.assign_team_classifier(frames, tracks)

        for frame_number, player_track in enumerate(tracks["players"]):
            team_assigner.get_player_crops(frames[frame_number], 
                                            player_track, 
                                            frame_number, 
                                            tracks)
    
    if load_pkl:
        with open(f"./outputs/team_ball_control.pkl", "rb") as f:
            team_ball_control = pickle.load(f)
    else:
        player_assigner = PlayerBallAssigner()
        team_ball_control = []

        for frame_number, player_track in enumerate(tracks["players"]):
            ball_bbox = tracks["ball"][frame_number][1]["bbox"]
            assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)

            if assigned_player != -1:
                tracks["players"][frame_number][assigned_player]["has_control"] = True
                team_ball_control.append(tracks["players"][frame_number][assigned_player]["team"])
            else:
                try:
                    team_ball_control.append(team_ball_control[-1])
                except:
                    team_ball_control.append(1)
        team_ball_control = np.array(team_ball_control)
    # print(len(tracks["players"]))

        # Giải phóng bộ nhớ
        tracker.release()
        team_assigner.release()

        # os.makedirs("./outputs/", exist_ok=True)
        # with open("./outputs/tracks.pkl", "wb") as f:
        #     pickle.dump(tracks, f)
        save_pkl("tracks.pkl", tracks)
        save_pkl("team_ball_control.pkl", team_ball_control)
        save_pkl("camera_movement_frames.pkl", camera_movement_frames)
    
    option_frames = {
        "circle": [],
        "voronoi": [],
        "line": []
    }
    
    output_video_frames = tracker.draw_annotation(frames, tracks, team_ball_control, option_frames)

    output_video_frames = camera_movement.draw_camera_movement(output_video_frames, camera_movement_frames)

    output_video_frames = speed_and_distance.draw_speed_and_distance(output_video_frames, tracks)

    # output_path = "./outputs/output.avi"
    output_path = video_path.replace("inputs", "outputs").replace(".mp4", ".mp4")

    write_video(output_path, output_video_frames)

    circle_path = output_path.replace(".mp4", "_circle.mp4")
    voronoi_path = output_path.replace(".mp4", "_voronoi.mp4")
    line_path = output_path.replace(".mp4", "_line.mp4")

    path_backend = [output_path, circle_path, voronoi_path, line_path]

    write_video(
        circle_path,
        option_frames["circle"]
    )
    write_video(
        voronoi_path,
        option_frames["voronoi"]
    )
    write_video(
        line_path,
        option_frames["line"]
    )
    return path_backend, tracks

if __name__ == "__main__":
    # app.run(host="0.0.0.0",debug=True)
    video_path = "./inputs/ok_798b45_0.mp4"

    # Chú ý thông số load_pkl, lần đầu để False để tạo file .pkl, lần sau là True để đọc file .pkl
    output_path, tracks = process(video_path, load_pkl=True)