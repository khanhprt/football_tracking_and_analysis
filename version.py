import cv2
import supervision as sv

cap = cv2.VideoCapture("./inputs/ok_798b45_0.mp4")
count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    count += 1
    if count % 10 == 0:
        cv2.imwrite(f"./frames/frame_{count}.jpg", frame)
    # cv2.imshow("frame", frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
cap.release()
cv2.destroyAllWindows()

sv.crop_images()
