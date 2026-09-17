import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from gestures import detect_gesture

import tkinter as tk
from tkinter import filedialog
import fitz
from PIL import Image, ImageTk


class PDFViewer:

    def __init__(self, root):

        self.cap = cv2.VideoCapture(0)

        self.detector = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=python.BaseOptions(
                    model_asset_path="hand_landmarker.task"
                ),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=1
            )
        )

        self.timestamp = 0
        self.last_y = None

        self.update_camera()
        self.root = root
        self.root.title("MagicRead")

        self.doc = None
        self.page_num = 0
        self.zoom = 1.5

        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<Configure>", self.on_resize)

        scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=scrollbar.set)


        controls = tk.Frame(root)
        controls.pack()

        tk.Button(controls, text="Open", command=self.open_pdf).pack(side="left")
        tk.Button(controls, text="Previous", command=self.previous_page).pack(side="left")
        tk.Button(controls, text="Next", command=self.next_page).pack(side="left")
        tk.Button(controls, text="Zoom +", command=self.zoom_in).pack(side="left")
        tk.Button(controls, text="Zoom -", command=self.zoom_out).pack(side="left")

    def update_camera(self):

        success, frame = self.cap.read()

        if success:
            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            self.timestamp += 1

            result = self.detector.detect_for_video(
                image,
                self.timestamp
            )

            if result.hand_landmarks:

                hand = result.hand_landmarks[0]
                gesture = detect_gesture(hand)

                if gesture == "PINCH":

                    y = hand[8].y

                    if self.last_y is not None:

                        movement = y - self.last_y

                        if movement < -0.01:
                            self.scroll(-3)

                        elif movement > 0.01:
                            self.scroll(3)

                    self.last_y = y

                else:
                    self.last_y = None

        self.root.after(10, self.update_camera)
        
    def on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(
                int(-event.delta / 120),
                "units"
        )

    def on_resize(self, event):
        if self.doc:
            self.show_page()

    def open_pdf(self):
        path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )

        if path:
            self.doc = fitz.open(path)
            self.page_num = 0
            self.show_page()

    def show_page(self):
        if not self.doc:
            return

        self.canvas.delete("all")
        self.photos = []
        canvas_width = self.canvas.winfo_width()

        y = 20

        for page in self.doc:
            matrix = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=matrix)

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            photo = ImageTk.PhotoImage(image)
            self.photos.append(photo)
            
            x = max(20, (canvas_width - pix.width) // 2)

            self.canvas.create_image(
                x,
                y,
                anchor="nw",
                image=photo
            )

            y += pix.height + 20

        self.canvas.config(
            scrollregion=self.canvas.bbox("all")
        )

    def next_page(self):
        if self.doc and self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.show_page()

    def previous_page(self):
        if self.doc and self.page_num > 0:
            self.page_num -= 1
            self.show_page()

    def zoom_in(self):
        self.zoom += 0.2
        self.show_page()

    def zoom_out(self):
        if self.zoom > 0.4:
            self.zoom -= 0.2
            self.show_page()

    def scroll(self, amount):
        self.canvas.yview_scroll(amount, "units")


root = tk.Tk()
root.geometry("1000x700")

viewer = PDFViewer(root)

root.mainloop()