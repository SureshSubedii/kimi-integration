import cv2

image_path = "iiii.png" 
image = cv2.imread(image_path)

original_height, original_width = image.shape[:2]

issues=[
 {
                "height": 400,
                "label": "acne",
                "width": 400,
                "x": 210,
                "y": 150
            }
            ]
for issue in issues:
    x, y, w, h = issue["x"], issue["y"], issue["width"], issue["height"]
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green box
    cv2.putText(image, issue["label"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.namedWindow("Image with Bounding Boxes", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image with Bounding Boxes", original_width, original_height) 

cv2.imshow("Image with Bounding Boxes", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
