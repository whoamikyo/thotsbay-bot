from os.path import dirname, join, realpath
from random import randrange
from subprocess import call

from logger import get_logger
from Utils.utils import get_video_duration, image_uploader, thumbnails_path

log = get_logger(__name__)


class Thumbmaker:
    def __init__(self, options={}):

        self.path = dirname(realpath(__file__))
        self.options = {
            "dimension": options.get("dimension", "3x4"),
            "width": options.get("width", 1150),
        }

    def get_thumb_upload(self, input: str, name):

        duration = int(get_video_duration(input))
        log.debug(f"Duration: {duration}")
        shots = (lambda x: x[0] * x[1])(
            list(map(int, self.options["dimension"].split("x")))
        )
        log.debug(f"Shots: {shots}")
        shotlist = []
        for _ in range(3):
            frame = randrange(duration)
            log.debug(f"Frame: {frame}")
            shotlist.append(join(thumbnails_path, f"{name}{frame:06d}.jpg"))
            log.debug(f"Shotlist: {name}{frame:06d}.jpg")
            call(
                [
                    "ffmpeg",
                    "-ss",
                    str(frame),
                    "-v",
                    "error",
                    "-i",
                    input,
                    "-vframes",
                    "1",
                    shotlist[-1],
                    "-y",
                    "-vf",
                    "fps=fps=1/1",
                    "-pred",
                    "mixed",
                    "-q:v",
                    "10",
                ]
            )
            if len(shotlist) > 2:
                imgur_urls = image_uploader(shotlist)
                log.debug(f"Imgur urls: {imgur_urls}")
                return imgur_urls


if __name__ == "__main__":

    # Run python -m Utils.thumb_maker
    path = ""
    name = "teste"

    Thumbmaker().get_thumb_upload(path, name)
