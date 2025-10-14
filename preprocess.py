from pytesseract import Output, TesseractError, image_to_osd
from deskew import determine_skew
from skimage.transform import rotate as sk_rotate
import numpy as np
from PIL import Image
import time


def preprocess_image(image_path=None, image=None):
    if image is None and image_path is not None:
        image = Image.open(image_path)
    try:
        osd = image_to_osd(image, output_type=Output.DICT)
        rotate_angle = osd.get("rotate", 0)
    except TesseractError:
        rotate_angle = 0

    if rotate_angle != 0 and image is not None:
        image = image.rotate(-rotate_angle, expand=True)

    grayscale = image.convert("L")
    skew_angle = determine_skew(np.array(grayscale))

    if skew_angle is not None and abs(skew_angle) > 0.1:
        rotated = sk_rotate(np.array(image), skew_angle, resize=True) * 255
        image = Image.fromarray(rotated.astype(np.uint8))

    return image


start = time.perf_counter()
img = Image.open("demo/images/image.png")
preprocessed_image = preprocess_image(image=img)
preprocessed_image.save("demo/images/preprocessed_image.png")
end = time.perf_counter()

print(f"Preprocessing took {end - start:.2f} seconds")
