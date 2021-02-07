class object_detection:
    # size of detection area
    img_size = (1200, 1200)
    millimeter = img_size[0] / 120  # Pixel / millimeter
    max_length_insect = 4
    top_left = (int(millimeter * 10), int(millimeter * 10))
    bottom_right = (int(img_size[0] - (millimeter * 10)), \
        int(img_size[1] - (millimeter * 10)))
    height = bottom_right[0] - top_left[0]
    radius = 0.25       # Parameter for corners
    corner_radius = int((height / 2) * radius)
    counter = 0

    def __init__(self, img):

        self.img = img
        # lists for coordinates
        self.center = []
        self.center_2 = []


    # function for round rectangle
    def rounded_rectangle(self, img, top_left, bottom_right, \
            radius=0, color=(255, 0, 0), thickness=1):
        
        p1 = top_left
        p2 = (bottom_right[1], top_left[1])
        p3 = (bottom_right[1], bottom_right[0])
        p4 = (top_left[0], bottom_right[0])
        height = abs(bottom_right[0] - top_left[1])

        corner_radius = int(radius * (height / 2))
        cv.line(img, (p1[0] + corner_radius, p1[1]), \
            (p2[0] - corner_radius, p2[1]), color, thickness)
        cv.line(img, (p2[0], p2[1] + corner_radius), \
            (p3[0], p3[1] - corner_radius), color, thickness)
        cv.line(img, (p3[0] - corner_radius, p4[1]), \
            (p4[0] + corner_radius, p3[1]), color, thickness)
        cv.line(img, (p4[0], p4[1] - corner_radius), \
            (p1[0], p1[1] + corner_radius), color, thickness)
        cv.ellipse(img, (p1[0] + corner_radius, p1[1] + corner_radius), \
            (corner_radius, corner_radius), 180, 0, 90, \
                color ,thickness)
        cv.ellipse(img, (p2[0] - corner_radius, p2[1] + corner_radius), \
            (corner_radius, corner_radius), 270, 0, 90, \
                color , thickness)
        cv.ellipse(img, (p3[0] - corner_radius, p3[1] - corner_radius), \
            (corner_radius, corner_radius), 0, 0, 90, \
                color , thickness)
        cv.ellipse(img, (p4[0] + corner_radius, p4[1] - corner_radius), \
            (corner_radius, corner_radius), 90, 0, 90, \
                color , thickness)

        return img


    # function for arc-region
    def arcs(self, x, y) -> bool:

        # upper left
        def arc_y_ul(x, y):
            x_0 = self.top_left[0] + self.corner_radius
            y_0 = self.top_left[1] + self.corner_radius
            if x > self.top_left[0] and x < (self.top_left[0] + \
                self.corner_radius) and y > self.top_left[1] and \
                    y < (self.top_left[1] + self.corner_radius):
                if y > (-1 * math.sqrt(self.corner_radius ** 2 - \
                    ((x - x_0) ** 2)) + y_0):
                    return True
                else:
                    return False

        # upper right
        def arc_y_ur(x, y):
            x_0 = self.top_left[0] + self.height - self.corner_radius
            y_0 = self.top_left[1] + self.corner_radius
            if x > (self.top_left[0] + self.height - self.corner_radius) \
                 and x < (self.top_left[0] + self.height) and \
                     y > self.top_left[1] and \
                         y < (self.top_left[1] + self.corner_radius):
                if y > (-1 * math.sqrt(self.corner_radius ** 2 - \
                    ((x - x_0) ** 2)) + y_0):
                    return True
                else:
                    return False

        #lower left
        def arc_y_ll(x, y):
            x_0 = self.top_left[0] + self.corner_radius
            y_0 = self.top_left[1] + self.height - self.corner_radius
            if x > self.top_left[0] and \
                x < (self.top_left[0] + self.corner_radius) and \
                    y > (self.top_left[0] + self.height - self.corner_radius) \
                        and y < (self.top_left[1] + self.height):
                if y < (math.sqrt(self.corner_radius ** 2 - \
                    ((x - x_0) ** 2)) + y_0):
                    return True
                else:
                    return False

        # lower right
        def arc_y_lr(x, y):
            x_0 = self.top_left[0] + self.height - self.corner_radius
            y_0 = self.top_left[1] + self.height - self.corner_radius
            if x > (self.top_left[0] + self.height - self.corner_radius) and \
                x < (self.top_left[0] + self.height) and \
                    y > (self.top_left[1] + self.height - self.corner_radius) \
                        and y < (self.top_left[1] + self.height):
                if y < (math.sqrt(self.corner_radius ** 2 - \
                    ((x - x_0) ** 2)) + y_0):
                    return True
                else:
                    return False
        if arc_y_ul(x, y) or \
            arc_y_ur(x, y) or \
            arc_y_ll(x, y) or \
            arc_y_lr(x, y):
            return True
        else:
            return False


    # image preprocessing
    def img_preprocessing(self, img):

        orig_img = cv.resize(img, (self.img_size[0], self.img_size[1]))
        self.rounded_rectangle(orig_img, self.top_left, self.bottom_right, \
            color=(255, 0, 0), radius=self.radius, thickness=3)
        orig_img = cv.medianBlur(orig_img, 5)
        orig_img_gray = cv.cvtColor(orig_img, cv.COLOR_BGR2GRAY)
        thresh = cv.adaptiveThreshold(orig_img_gray, 255, \
            cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 29, 20)
        contours, _ = cv.findContours(thresh, cv.RETR_TREE, \
            cv.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=lambda x: cv.contourArea(x), \
            reverse=True)

        # calculate size of object, center coordinates and check for conditions
        for cnt in contours:
            area = cv.contourArea(cnt)
            (x, y, w, h) = cv.boundingRect(cnt)
            if area >= 1 and area <= 300:
                M = cv.moments(cnt)
                c_X = int(M["m10"] / M["m00"])  # x-coordinate of center point
                c_Y = int(M["m01"] / M["m00"])  # y-coordinate of center point
                if self.arcs(x=c_X, y=c_Y) \
                    or (c_X >= (self.top_left[0] + self.corner_radius) and \
                        c_X <= (self.top_left[0] + self.height - \
                            self.corner_radius) or \
                                c_Y >= (self.top_left[1] + self.corner_radius)\
                                    and c_Y <= (self.top_left[1] + self.height\
                                         - self.corner_radius)) \
                    and not (c_X <= self.top_left[0] or \
                        c_X >= (self.top_left[0] + self.height)) and not \
                             (c_Y <= self.top_left[1] or \
                                 c_Y >= (self.top_left[1] + self.height)):
                    self.center_2.append([c_X, c_Y])
        
        return orig_img


    def distance(self, img) -> bool:

        # calculate distance matrix
        if self.center_2:
            center_2 = np.array(self.center_2)
            dist = distance.cdist(self.center_2, self.center_2, 'euclidean')
            dist = np.array(dist).tolist()
            center_2 = np.array(self.center_2).tolist()
        else:
            print("No insects in the petri dish!")
            return False

        # check distance to other objects
        j = 0
        counter = 0
        for l in dist:
            l.remove(0)
            for i in l:
                if i < self.millimeter * self.max_length_insect:
                    j += 1
                    break
            else:
                self.center.append(self.center_2[j])
                cv.circle(img, (self.center[counter][0], \
                    self.center[counter][1]), int(self.millimeter * 2), \
                        (0, 255, 255), 2)
                j += 1
                counter += 1
        print("Number of insects = " + str(counter))
        print("Coordinates of the insects to be pipetted: ")
        print(self.center)
        
        return True


    def show_img(self, img):
        cv.cvtColor(img, cv.COLOR_RGB2BGR)
        cv.namedWindow('image_insects', cv.WINDOW_NORMAL)
        cv.imshow('image_insects', img)
        cv.waitKey(0)
        cv.destroyAllWindows()
        self.counter += 1
