class Cam:
    counter = -1
    def __init__(self):
        self.camera = xiapi.Camera()
        self.img = xiapi.Image()
        self.camera.open_device()
        self.camera.set_param('exposure', 30000)
        self.camera.set_imgdataformat('XI_RGB32')
        Cam.counter += 1

    def take_img(self):
        self.camera.start_acquisition()
        self.camera.get_image(self.img)
        cam_data = self.img.get_image_data_numpy()
        self.counter += 1
        self.camera.stop_acquisition()
        self.camera.close_device()
        return cam_data
        