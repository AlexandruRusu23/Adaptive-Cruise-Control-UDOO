"""
Analyser module
"""
import threading
import time
import cv2
import numpy as np
import numpy.matlib

# Region-of-interest vertices
# We want a trapezoid shape, with bottom edge at the bottom of the image
TRAPEZOID_BOTTOM_WIDTH = 1.2
TRAPEZOID_TOP_WIDTH = 0.38
TRAPEZOID_HEIGHT = 0.9

# Hough Transform
HOUGH_DIST_RESOLUTION = 2 # distance resolution in pixels of the Hough grid
ANGULAR_RESOLUTION = 1 * np.pi/180 # angular resolution in radians of the Hough grid
HOUGH_THRESHOLD = 20 # minimum number of votes (intersections in Hough grid cell)
MIN_LINE_LENGHT = 25 #minimum number of pixels making up a line
MAX_LINE_GAP = 10	# maximum gap in pixels between connectable line segments

ALPHA = 0.8
BETA = 1.
GAMMA = 0.

RIGHT_X1_COORD = 1
LEFT_X1_COORD = 1
Y1_COORD = 1

class Analyser(object):
    """
    Analyser class
    - responsible to analyse the current frame
    - detect lanes, cars, obstacles, road signs, etc
    and send the commands to SerialManager
    """
    def __init__(self):
        self.__current_frame = None
        self.__encode_parameter = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
        self.__command_timer = 0

        self.__go_forward = False
        self.__go_left = False
        self.__go_right = False

        self.__lines_coords_list = []

    def analyse(self, frame_queue, autonomous_states_queue, commands_queue, analysed_frame_queue):
        """
        get the current frame from FRAME_QUEUE of CarManager and analyse
        """
        current_thread = threading.currentThread()
        self.__command_timer = time.time()
        while getattr(current_thread, 'is_running', True):
            string_data = frame_queue.get(True, None)
            frame = numpy.fromstring(string_data, dtype='uint8')
            self.__current_frame = cv2.imdecode(frame, 1)
            frame_queue.task_done()

            if getattr(current_thread, 'is_analysing', True):
                self.__lane_assist(autonomous_states_queue, commands_queue)
                result, encrypted_image = \
                    cv2.imencode('.jpg', self.__current_frame, self.__encode_parameter)
                if bool(result) is False:
                    break
                analysed_frame = numpy.array(encrypted_image)
                analysed_frame_queue.put(analysed_frame)
            else:
                result, encrypted_image = \
                    cv2.imencode('.jpg', self.__current_frame, self.__encode_parameter)
                if bool(result) is False:
                    break
                analysed_frame = numpy.array(encrypted_image)
                analysed_frame_queue.put(analysed_frame.tostring(), True, None)

            #autonomous_states_queue.put()
            #commands_queue.put()

    def __gaussian_blur(self, img, kernel_size=3):
        """Applies a Gaussian Noise kernel"""
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

    def __grayscale(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def __canny(self, image, sigma=0.33):
        """Applies the Canny transform"""
        median_variable = np.median(image)

        lower = int(max(0, (1.0 - sigma) * median_variable))
        upper = int(min(255, (1.0 + sigma) * median_variable))
        edged = cv2.Canny(image, lower, upper)

        return edged

    def __region_of_interest(self, img, vertices):

        mask = np.zeros_like(img)

        if len(img.shape) > 2:
            channel_count = img.shape[2]
            ignore_mask_color = (255,) * channel_count
        else:
            ignore_mask_color = 255

        cv2.fillPoly(mask, vertices, ignore_mask_color)

        masked_image = cv2.bitwise_and(img, mask)
        return masked_image

    def __draw_lines(self, img, lines, color=[255, 0, 0], thickness=5):
        if lines is None:
            return
        if len(lines) == 0:
            return
        draw_right = True
        draw_left = True

        slope_threshold = 0.5
        slopes = []
        new_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]  # line = [[x1, y1, x2, y2]]

            if x2 - x1 == 0.:  # corner case, avoiding division by 0
                slope = 999.  # practically infinite slope
            else:
                slope = (y2 - y1) / (x2 - x1)

            if abs(slope) > slope_threshold:
                slopes.append(slope)
                new_lines.append(line)

        lines = new_lines

        right_lines = []
        left_lines = []
        for i, line in enumerate(lines):
            x1, y1, x2, y2 = line[0]
            img_x_center = img.shape[1] / 2  # x coordinate of center of image
            if slopes[i] > 0 and x1 > img_x_center and x2 > img_x_center:
                right_lines.append(line)
            elif slopes[i] < 0 and x1 < img_x_center and x2 < img_x_center:
                left_lines.append(line)

        right_lines_x = []
        right_lines_y = []

        for line in right_lines:
            x1, y1, x2, y2 = line[0]

            right_lines_x.append(x1)
            right_lines_x.append(x2)

            right_lines_y.append(y1)
            right_lines_y.append(y2)

        if len(right_lines_x) > 0:
            right_m, right_b = np.polyfit(right_lines_x, right_lines_y, 1)  # y = m*x + b
        else:
            right_m, right_b = 1, 1
            draw_right = False

        left_lines_x = []
        left_lines_y = []

        for line in left_lines:
            x1, y1, x2, y2 = line[0]

            left_lines_x.append(x1)
            left_lines_x.append(x2)

            left_lines_y.append(y1)
            left_lines_y.append(y2)

        if len(left_lines_x) > 0:
            left_m, left_b = np.polyfit(left_lines_x, left_lines_y, 1)  # y = m*x + b
        else:
            left_m, left_b = 1, 1
            draw_left = False

        y1 = img.shape[0]
        y2 = img.shape[0] * (1 - TRAPEZOID_HEIGHT)

        right_x1 = (y1 - right_b) / right_m
        right_x2 = (y2 - right_b) / right_m

        left_x1 = (y1 - left_b) / left_m
        left_x2 = (y2 - left_b) / left_m

        y1 = int(y1)
        y2 = int(y2)
        right_x1 = int(right_x1)
        right_x2 = int(right_x2)
        left_x1 = int(left_x1)
        left_x2 = int(left_x2)

        if draw_right:
            cv2.line(img, (right_x1, y1), (right_x2, y2), color, thickness)

        if draw_left:
            cv2.line(img, (left_x1, y1), (left_x2, y2), color, thickness)

        self.__lines_coords_list = []
        self.__lines_coords_list.append((left_x1, y1))
        self.__lines_coords_list.append((left_x2, y2))
        self.__lines_coords_list.append((right_x1, y1))
        self.__lines_coords_list.append((right_x2, y2))

        global RIGHT_X1_COORD
        global Y1_COORD
        global LEFT_X1_COORD

        RIGHT_X1_COORD = right_x1
        Y1_COORD = y1
        LEFT_X1_COORD = left_x1

    def __hough_lines(self, img, HOUGH_DIST_RESOLUTION, ANGULAR_RESOLUTION, HOUGH_THRESHOLD, min_line_len, MAX_LINE_GAP):
        lines = cv2.HoughLinesP(img, HOUGH_DIST_RESOLUTION, ANGULAR_RESOLUTION, HOUGH_THRESHOLD, np.array([]), \
            minLineLength=min_line_len, maxLineGap=MAX_LINE_GAP)

        (x1, x2) = img.shape
        dt = np.dtype(np.uint8)
        line_img = np.zeros((x1, x2, 3), dt)
        self.__draw_lines(line_img, lines)

        return line_img

    def __lane_assist(self, autonomous_states_queue, commands_queue):
        grey = self.__grayscale(self.__current_frame)
        blur_grey = self.__gaussian_blur(grey)

        edges = self.__canny(blur_grey)

        imshape = self.__current_frame.shape
        vertices = np.array([[\
			((imshape[1] * (1 - TRAPEZOID_BOTTOM_WIDTH)) // 2, imshape[0]),\
			((imshape[1] * (1 - TRAPEZOID_TOP_WIDTH)) // 2, imshape[0] - imshape[0] * TRAPEZOID_HEIGHT),\
			(imshape[1] - (imshape[1] * (1 - TRAPEZOID_TOP_WIDTH)) // 2, imshape[0] - imshape[0] * TRAPEZOID_HEIGHT),\
			(imshape[1] - (imshape[1] * (1 - TRAPEZOID_BOTTOM_WIDTH)) // 2, imshape[0])]]\
			, dtype=np.int32)

        masked_image = self.__region_of_interest(edges, vertices)

        line_image = self.__hough_lines(masked_image, HOUGH_DIST_RESOLUTION, ANGULAR_RESOLUTION, \
            HOUGH_THRESHOLD, MIN_LINE_LENGHT, MAX_LINE_GAP)

        final_image = self.__current_frame.astype('uint8')

        cv2.addWeighted(self.__current_frame, ALPHA, line_image, BETA, GAMMA, final_image)

        final_image2 = final_image.astype('uint8')

        final_x = (RIGHT_X1_COORD + LEFT_X1_COORD)/2

        cv2.circle(final_image2, (final_x, Y1_COORD), 50, [255, 0, 0], 5)

        height, width, channels = self.__current_frame.shape

        if time.time() - self.__command_timer > 0.1:

            if len(self.__lines_coords_list) > 3:
                left_median_x = \
                    (self.__lines_coords_list[0][0] + self.__lines_coords_list[1][0]) / 2
                right_median_x = \
                    (self.__lines_coords_list[2][0] + self.__lines_coords_list[3][0]) / 2
                if left_median_x > 30 * width / 100:
                    if bool(self.__go_right) is False:
                        commands_queue.put('5/')
                        self.__go_forward = False
                        self.__go_right = True
                elif right_median_x < 70 * width / 100:
                    if bool(self.__go_left) is False:
                        commands_queue.put('4/')
                        self.__go_forward = False
                        self.__go_left = True
                else:
                    if bool(self.__go_forward) is False:
                        commands_queue.put('1/1/')
                        self.__go_forward = True
                        self.__go_left = False
                        self.__go_right = False

        self.__current_frame = final_image2
