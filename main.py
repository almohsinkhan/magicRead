import math
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

        self.root = root
        self.root.title("MagicRead")

        self.doc = None
        self.page_num = 0
        self.zoom = 1.5
        self.photos = []
        self.last_zoom_distance = None
        self.cursor_x = 0
        self.cursor_y = 0
        self.cursor_id = None

        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack(fill="both", expand=True)

        self.cursor_id = self.canvas.create_oval(
                    0, 0, 20, 20,
                    fill="red"
                )
        
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<Configure>", self.on_resize)

        scrollbar = tk.Scrollbar(
            root,
            orient="vertical",
            command=self.canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.canvas.config(
            yscrollcommand=scrollbar.set
        )

        controls = tk.Frame(root)
        controls.pack()

        tk.Button(
            controls,
            text="Open",
            command=self.open_pdf
        ).pack(side="left")

        tk.Button(
            controls,
            text="Previous",
            command=self.previous_page
        ).pack(side="left")

        tk.Button(
            controls,
            text="Next",
            command=self.next_page
        ).pack(side="left")

        tk.Button(
            controls,
            text="Zoom +",
            command=self.zoom_in
        ).pack(side="left")

        tk.Button(
            controls,
            text="Zoom -",
            command=self.zoom_out
        ).pack(side="left")

        self.cap = cv2.VideoCapture(0)

        self.detector = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=python.BaseOptions(
                    model_asset_path="hand_landmarker.task"
                ),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=2,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
        )

        self.timestamp = 0
        self.last_y = None

        # Start camera loop
        self.update_camera()

    def move_cursor(self, hand):

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        x = int(hand[8].x * width)
        y = int(hand[8].y * height)

        self.canvas.coords(
            self.cursor_id,
            x - 10,
            y - 10,
            x + 10,
            y + 10
        )
            

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

            # -------- TWO HANDS: ZOOM --------
            if len(result.hand_landmarks) == 2:

                hand1 = result.hand_landmarks[0]
                hand2 = result.hand_landmarks[1]

                p1 = hand1[8]
                p2 = hand2[8]

                distance = math.hypot(
                    p1.x - p2.x,
                    p1.y - p2.y
                )

                if self.last_zoom_distance is not None:

                    change = distance - self.last_zoom_distance

                    if change > 0.05:
                        self.zoom_in()

                    elif change < -0.05:
                        self.zoom_out()

                self.last_zoom_distance = distance
                self.last_y = None

            # -------- ONE HAND: GESTURES --------
            elif len(result.hand_landmarks) == 1:

                self.last_zoom_distance = None

                hand = result.hand_landmarks[0]

                gesture = detect_gesture(hand)

                if gesture == "POINT":
                    
                    self.move_cursor(hand)

                elif gesture == "PINCH":

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

            else:

                self.last_y = None
                self.last_zoom_distance = None

        self.root.after(10, self.update_camera)


    def scroll(self, amount):

        self.canvas.yview_scroll(
            amount,
            "units"
        )

    def on_mousewheel(self, event):

        if event.num == 4:

            self.canvas.yview_scroll(
                -3,
                "units"
            )

        elif event.num == 5:

            self.canvas.yview_scroll(
                3,
                "units"
            )

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
            filetypes=[
                ("PDF files", "*.pdf")
            ]
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

            matrix = fitz.Matrix(
                self.zoom,
                self.zoom
            )

            pix = page.get_pixmap(
                matrix=matrix
            )

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            photo = ImageTk.PhotoImage(image)

            self.photos.append(photo)

            x = max(
                20,
                (canvas_width - pix.width) // 2
            )

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


    def close(self):

        self.cap.release()

        self.detector.close()

        self.root.destroy()



root = tk.Tk()

root.geometry("1000x700")

viewer = PDFViewer(root)

root.protocol(
    "WM_DELETE_WINDOW",
    viewer.close
)

root.mainloop()