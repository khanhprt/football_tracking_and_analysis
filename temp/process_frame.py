import cv2
import pickle
import os

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    count = 0
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count > 150:
            break
        count += 1
        frames.append(frame)
    return frames

def write_video(output_path, out_put_frame):
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, 24, (out_put_frame[0].shape[1], out_put_frame[0].shape[0]))
    for i in range(len(out_put_frame)):
        out.write(out_put_frame[i])
        # cv2.imshow("Output", out_put_frame[i])
        # if cv2.waitKey(0) & 0xFF == ord('q'):
        #     break

    # cv2.destroyAllWindows()
    out.release()

def save_pkl(name, value):

    os.makedirs("./outputs/", exist_ok=True)
    with open(f"./outputs/{name}", "wb") as f:
        pickle.dump(value, f)

