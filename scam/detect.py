import cv2
import numpy
from scam import pipe

class NoFrameContentError(Exception):
    """
    No frame content currently available
    """
    pass


class ContourMatcher(pipe.Pipe):
    """
    Detects contours and continues if there's enough matching contours
    """
    BLUR_SIZE = 11
    THRESHOLD_SENSITIVITY = 50
    PREVIOUS_FRAME = 'CONTOUR_MATCHER_PREVIOUS_FRAME'
    PREVIOUS_FRAME_GRAY = 'CONTOUR_MATCHER_PREVIOUS_FRAME_GRAY'

    def __init__(self, minimum_area=300, show_contours=False):
        self.minimum_area = minimum_area
        self.show_contours = show_contours

    def run(self, context, next_run):
        if 'SOURCE_RAW_CONTENT' not in context:
            raise NoFrameContentError()
        current_array = numpy.frombuffer(context['SOURCE_RAW_CONTENT'], dtype=numpy.uint8)
        current_frame = cv2.imdecode(current_array, flags=cv2.IMREAD_COLOR)
        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.GaussianBlur(current_gray, (ContourMatcher.BLUR_SIZE, ContourMatcher.BLUR_SIZE), 0)

        if ContourMatcher.PREVIOUS_FRAME not in context:
            context[ContourMatcher.PREVIOUS_FRAME] = current_frame
            context[ContourMatcher.PREVIOUS_FRAME_GRAY] = current_gray
            return

        # do the matching
        previous_frame = context[ContourMatcher.PREVIOUS_FRAME]
        previous_gray = context[ContourMatcher.PREVIOUS_FRAME_GRAY]
        frame_delta = cv2.absdiff(current_gray, previous_gray)
        _, threshold = cv2.threshold(frame_delta, ContourMatcher.THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY)

        # Fill in small shapes where possible
        threshold = cv2.dilate(threshold, None, iterations=2)

        # find the outer edges of the contours
        (im2, contours, hierarchy) = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contoured_frame = current_frame.copy()
        matched = False
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= self.minimum_area:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(contoured_frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                matched = True

        context[ContourMatcher.PREVIOUS_FRAME] = current_frame
        context[ContourMatcher.PREVIOUS_FRAME_GRAY] = current_gray

        if matched:
            if self.show_contours:
                _, content = cv2.imencode(context['SOURCE_EXTENSION'], contoured_frame)
                context['SOURCE_RAW_CONTENT'] = content.tostring()
            return next_run()
