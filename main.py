import time
import cv2
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk
import imutils


class App:
    """
    В данном коде создается GUI приложения с использованием tkinter,
    которое позволяет запускать и останавливать захват видео с камеры,
    а также склеивать захваченные кадры и записывать результат в изображение.
    """
    def __init__(self, master):
        """
        Initialize the GUI and the video capturing.

        :param master: the tkinter window
        """
        self.master = master
        self.master.title("Real-time image stitching")
        self.master.geometry("800x600")

        self.capture = None
        self.frames = []
        self.is_capturing = False
        self.stitching_complete = False

        self.start_button = tk.Button(self.master, text="Start", command=self.start_capture)
        self.start_button.pack(pady=10)
        self.stop_button = tk.Button(self.master, text="Stop", command=self.stop_capture, state="disabled")
        self.stop_button.pack(pady=10)
        self.stitch_button = tk.Button(self.master, text="Stitch", command=self.stitch_images, state="disabled")
        self.stitch_button.pack(pady=10)

        self.video_label = tk.Label(self.master)
        self.video_label.pack()

    def start_capture(self):
        """
        Start capturing video frames.
        """
        self.capture = cv2.VideoCapture(0)
        self.is_capturing = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.stitch_button.config(state="disabled")

        self.capture_thread = Thread(target=self.update_frames)
        self.capture_thread.start()

    def stop_capture(self):
        """
        Stop capturing video frames.
        """
        self.is_capturing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.stitch_button.config(state="normal")

    def update_frames(self):
        """
        Continuously update the video frames.
        """
        while self.is_capturing:
            time.sleep(1)
            _, frame = self.capture.read()
            self.frames.append(frame)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            self.image = Image.fromarray(cv2image)
            self.imgtk = ImageTk.PhotoImage(image=self.image)
            self.video_label.configure(image=self.imgtk)
            self.master.update()

    def stitch_images(self):
        """
        Stitch the captured frames and write the result to an image file.
        """
        imageStitcher = cv2.Stitcher_create()
        error, stitched_img = imageStitcher.stitch(self.frames)
        if not error:
            cv2.imwrite("stitchedOutput.png", stitched_img)
            gray = cv2.cvtColor(stitched_img, cv2.COLOR_BGR2GRAY)
            thresh_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
            contours = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)
            areaOI = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(areaOI)
            stitched_img = stitched_img[y:y + h, x:x + w]
            cv2.imwrite("stitchedOutputProcessed.png", stitched_img)
        else:
            print("Images could not be stitched!")
            print("Likely not enough keypoints being detected!")



root = tk.Tk()
app = App(master=root)
root.mainloop()