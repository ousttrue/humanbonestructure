import asyncio
import numpy
from ..eventproperty import EventProperty


class VideCapture:
    def __init__(self) -> None:
        self.frame_event: EventProperty[numpy.ndarray] = EventProperty()

    async def start_async(self):
        import cv2
        cap = cv2.VideoCapture(0)
        while True:
            success, image = await asyncio.to_thread(cap.read)
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            self.frame_event.set(image)
