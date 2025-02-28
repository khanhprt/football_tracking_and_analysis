import cv2

path = "inputs\ok_798b45_0.mp4"
cap = cv2.VideoCapture(path)
fourcc = cv2.VideoWriter_fourcc(*'avc1')
out = cv2.VideoWriter("test.mp4", fourcc, 24, (1920,1080))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Frame", frame)
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
out.release()
cv2.destroyAllWindows()



