SETUP_ID = {
    56:2, 60:4, 50:7, 58:15, 179:36, 244:15, 280:5, 278:9, 242:43, 247:43, 392:367
}


def measure_distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def measure_xy_distance(point1, point2):
    return point1[0] - point2[0], point1[1] - point2[1]

def get_center_of_bbox(bbox):
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int((y1 + y2) / 2)

def get_foot_position(bbox):
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int(y2)

def get_bbox_width(bbox):
    return bbox[2] - bbox[0]
