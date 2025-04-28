from crawler.utils import draw_points , sa
from PIL import Image
import numpy as np

path = ""
image = Image.open(path)     
image_np = np.asarray(image)
threshold_color = 230
# RGB 채널별로 한 번에 처리
# 행별로 모든 픽셀이 흰색인지 확인 (axis 1은 너비, axis 2는 채널)
white = image_np[:, :, :3].mean(axis=(1, 2)) > threshold_color
dark_pixels = [np.sum(row < 200) > 5 for row in np.mean(image_np, axis=2)]
width = image.width
final = ~np.array(dark_pixels) & white  # Changed from 'not dark_pixels' to '~np.array(dark_pixels)'
points = np.array([(width//2, idx) for idx, i in enumerate(final) if i])
draw_points(image, points)
image.save("test.png")

