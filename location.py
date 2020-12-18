import cv2


def locate():
    img = cv2.imread('./src.jpg', 0)
    re, img1 = cv2.threshold(img, 125, 255, 0)
    contours, b = cv2.findContours(img1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for j in range(0, len(contours) - 1):
        M = cv2.moments(contours[j])  # 计算第一条轮廓的各阶矩,字典形式
        try:
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
        except:
            continue
        area = cv2.contourArea(contours[j])
        if area < 6000 or area > 8000 or center_x < 500:
            continue
        return center_x
