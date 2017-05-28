"""
Analyser module
"""
import threading
import time
import cv2
import numpy as np
import numpy.matlib

import DetectChars
import DetectPlates
import PossiblePlate

SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False

# Region-of-interest vertices
# We want a trapezoid shape, with bottom edge at the bottom of the image
TRAPEZOID_BOTTOM_WIDTH = 1.2
TRAPEZOID_TOP_WIDTH = 0.65
TRAPEZOID_HEIGHT = 0.8

# Hough Transform
HOUGH_DIST_RESOLUTION = 1 # distance resolution in pixels of the Hough grid
ANGULAR_RESOLUTION = 1 * np.pi/180 # angular resolution in radians of the Hough grid
HOUGH_THRESHOLD = 50 # minimum number of votes (intersections in Hough grid cell)
MIN_LINE_LENGHT = 70 #minimum number of pixels making up a line
MAX_LINE_GAP = 60	# maximum gap in pixels between connectable line segments

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
    - send the commands to SerialManager via Controller queue
    - send analysed frames to StreamServer via queue
    - update user rights about controlling the car
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
        bln_knn_training_successful = DetectChars.loadKNNDataAndTrainKNN() # attempt KNN training
        if bool(bln_knn_training_successful) is False:
            return
        while getattr(current_thread, 'is_running', True):
            string_data = frame_queue.get(True, None)
            frame = numpy.fromstring(string_data, dtype='uint8')
            self.__current_frame = cv2.imdecode(frame, 1)

            if getattr(current_thread, 'is_analysing', True):
                self.__car_detection(commands_queue, autonomous_states_queue)
                self.__lane_assist(commands_queue)

            self.__draw_car_orientation()
            result, encrypted_image = \
                cv2.imencode('.jpg', self.__current_frame, self.__encode_parameter)

            if bool(result) is False:
                break

            analysed_frame = numpy.array(encrypted_image)
            analysed_frame_queue.put(analysed_frame.tostring())
            frame_queue.task_done()

            #autonomous_states_queue.put()

    def __draw_rect_around_plate(self, current_scene, lic_plate):
        p2f_rect_points = cv2.boxPoints(lic_plate.rrLocationOfPlateInScene)

        cv2.line(current_scene, tuple(p2f_rect_points[0]), \
            tuple(p2f_rect_points[1]), SCALAR_RED, 2)
        cv2.line(current_scene, tuple(p2f_rect_points[1]), \
            tuple(p2f_rect_points[2]), SCALAR_RED, 2)
        cv2.line(current_scene, tuple(p2f_rect_points[2]), \
            tuple(p2f_rect_points[3]), SCALAR_RED, 2)
        cv2.line(current_scene, tuple(p2f_rect_points[3]), \
            tuple(p2f_rect_points[0]), SCALAR_RED, 2)

        return p2f_rect_points

    def __draw_distance_to_car(self, lic_plate):
        height, width, channels = self.__current_frame.shape
        p2f_rect_points = cv2.boxPoints(lic_plate.rrLocationOfPlateInScene)
        distance_to_car = height - p2f_rect_points[3][1]
        distance_to_car = float("{0:.2f}".format(distance_to_car))
        distance_to_car = distance_to_car / 6.0
        distance_position = (2 * width / 100, 95 * height / 100)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(self.__current_frame, 'Distance:' + str(distance_to_car) + 'cm', \
            distance_position, font, 1, (0, 255, 255), 2, cv2.LINE_AA)

    def __car_detection(self, commands_queue, autonomous_states_queue):
        list_of_possible_plates = DetectPlates.detectPlatesInScene(self.__current_frame)

        list_of_possible_plates = DetectChars.detectCharsInPlates(list_of_possible_plates)

        list_of_possible_plates.sort(key=lambda possiblePlate: len(possiblePlate.strChars), \
            reverse=True)

        if len(list_of_possible_plates) > 0:
            plate_points = lic_plate = list_of_possible_plates[0]
            self.__draw_distance_to_car(lic_plate)
            self.__draw_rect_around_plate(self.__current_frame, lic_plate)

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

    def __draw_lines(self, img, lines, color=None, thickness=5):
        if color is None:
            color = [255, 0, 0]
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

    def __hough_lines(self, img):
        lines = cv2.HoughLinesP(img, HOUGH_DIST_RESOLUTION, ANGULAR_RESOLUTION, \
            HOUGH_THRESHOLD, np.array([]), minLineLength=MIN_LINE_LENGHT, maxLineGap=MAX_LINE_GAP)

        (x1, x2) = img.shape
        dt = np.dtype(np.uint8)
        line_img = np.zeros((x1, x2, 3), dt)
        self.__draw_lines(line_img, lines)

        return line_img

    def __draw_car_orientation(self):
        height, width, channels = self.__current_frame.shape

        pick_x_coord = width / 2
        pick_y_coord = 50 * height / 100
        pick_width = 20 * width / 100
        pick_height = 15 * height / 100
        base_width = 20 * width / 100
        base_height = 30 * height / 100

        car_arrow_vertex = []
        # varf sageata
        car_arrow_vertex.append([pick_x_coord, pick_y_coord])
        #colt dreapta triungi
        car_arrow_vertex.append([pick_x_coord + pick_width, pick_y_coord + pick_height])
        #colt dreapta-sus patrat
        car_arrow_vertex.append([pick_x_coord + base_width / 2, pick_y_coord + pick_height])
        #colt dreapta-jos patrat
        car_arrow_vertex.append([pick_x_coord + base_width, \
            pick_y_coord + pick_height + base_height])
        #colt stanga-jos patrat
        car_arrow_vertex.append([pick_x_coord - base_width, \
            pick_y_coord + pick_height + base_height])
        #colt stanga-sus patrat
        car_arrow_vertex.append([pick_x_coord - base_width / 2, pick_y_coord + pick_height])
        #colt stanga triunghi
        car_arrow_vertex.append([pick_x_coord - pick_width, pick_y_coord + pick_height])

        overlay = self.__current_frame.copy()

        pts = np.array(car_arrow_vertex, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillConvexPoly(overlay, pts, (0, 255, 255))
        alpha = 0.2
        cv2.addWeighted(overlay, alpha, self.__current_frame, 1 - alpha, 0, self.__current_frame)

    def __lane_assist(self, commands_queue):
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

        line_image = self.__hough_lines(masked_image)

        final_image = self.__current_frame.astype('uint8')

        cv2.addWeighted(self.__current_frame, ALPHA, line_image, BETA, GAMMA, final_image)

        final_image2 = final_image.astype('uint8')

        #height, width, channels = self.__current_frame.shape

        # if time.time() - self.__command_timer > 0.1:
        #     if len(self.__lines_coords_list) > 3:
        #         left_median_x = \
        #             (self.__lines_coords_list[0][0] + self.__lines_coords_list[1][0]) / 2
        #         right_median_x = \
        #             (self.__lines_coords_list[2][0] + self.__lines_coords_list[3][0]) / 2
        #         if left_median_x > 30 * width / 100:
        #             commands_queue.put('5/')
        #             self.__go_forward = False
        #         elif right_median_x < 70 * width / 100:
        #             commands_queue.put('4/')
        #             self.__go_forward = False
        #         else:
        #             if bool(self.__go_forward) is False:
        #                 commands_queue.put('1/1/')
        #                 self.__go_forward = True

        self.__current_frame = final_image2
