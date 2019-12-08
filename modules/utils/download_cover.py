def convert_image_to_jpg(image_path):
    import os
    from PIL import Image
    from pathlib import Path

    im = Image.open(image_path)
    rgb_im = im.convert('RGB')

    directory = Path(image_path).parent

    rgb_im.save('{}/cover.jpg'.format(directory))

    os.remove(image_path)


def download(image_url, save_filename):
    import requests
    import shutil

    response = requests.get(image_url, stream=True)

    with open(save_filename, 'wb') as writer:
        shutil.copyfileobj(response.raw, writer)

    convert_image_to_jpg(save_filename)

    del response
