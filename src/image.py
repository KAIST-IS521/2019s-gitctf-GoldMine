import cv2
from pathlib import Path
from tempfile import NamedTemporaryFile


def image_path(uid, is_new=False):
    filename = '{}.png'.format(uid)
    path = Path('.', 'user_image', filename)
    if not is_new and not path.exists():
        path = Path('.', 'user_image', '.default')
    return path

def get_image(uid):
    path = image_path(uid)
    img = cv2.imread(str(path))
    return img

def upload_image(uid, image_data):
    path = image_path(uid, True)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not image_data:
        if path.exists():
            path.unlink()
        return

    with NamedTemporaryFile() as tempsig:
        tempsig.write(image_data)
        tempsig.flush()
        img = cv2.imread(tempsig.name)

    cv2.imwrite(str(path), img, params=[cv2.IMWRITE_PNG_COMPRESSION, 0])
