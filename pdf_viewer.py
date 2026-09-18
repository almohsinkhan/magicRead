import tkinter as tk
from tkinter import filedialog

import fitz
from PIL import Image, ImageTk

from camera_controller import CameraController
from gesture_controller import GestureController


class PDFViewer:
    """Render and control a PDF in the Tkinter window."""

    ENABLE_CURSOR_CONTROL = False

    def __init__(self, root):
        self.root = root
        self.root.title("MagicRead")

        self.doc = None
        self.page_num = 0
        self.page = None
        self.zoom = 1.5
        self.photos = []

        self.cursor_x = 0
        self.cursor_y = 0
        self.cursor_id = None
        self.cursor_smoothing = 0.45

        self.pdf_x_screen = 20
        self.pdf_y_screen = 20

        self.create_interface()

        self.gesture_controller = GestureController(self)
        self.camera = CameraController(root, self.gesture_controller.handle_landmarks)
        self.camera.start()

    def create_interface(self):
        """Create the PDF canvas, scrolling controls, and buttons."""
        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(fill="both", expand=True)
        if self.ENABLE_CURSOR_CONTROL:
            self.cursor_id = self.canvas.create_oval(0, 0, 10, 10, fill="red")

        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<Configure>", self.on_resize)

        scrollbar = tk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.canvas.yview,
        )
        scrollbar.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=scrollbar.set)

        controls = tk.Frame(self.root)
        controls.pack()

        tk.Button(controls, text="Open", command=self.open_pdf).pack(side="left")
        tk.Button(controls, text="Previous", command=self.previous_page).pack(side="left")
        tk.Button(controls, text="Next", command=self.next_page).pack(side="left")
        tk.Button(controls, text="Zoom +", command=self.zoom_in).pack(side="left")
        tk.Button(controls, text="Zoom -", command=self.zoom_out).pack(side="left")

    def get_word_at_cursor(self):
        """Highlight the PDF word below the virtual cursor."""
        print("CURSOR:", self.cursor_x, self.cursor_y)

        if not self.doc:
            print("No PDF open")
            return

        self.doc.save("highlighted.pdf", garbage=4, deflate=True)

        page = self.doc[self.page_num]
        pdf_x = (self.cursor_x - self.pdf_x_screen) / self.zoom
        pdf_y = (self.cursor_y - self.pdf_y_screen) / self.zoom

        print("PAGE:", self.page_num)
        print("PDF POSITION:", pdf_x, pdf_y)

        for word in page.get_text("words"):
            x0, y0, x1, y1, text = word[:5]

            if x0 <= pdf_x <= x1 and y0 <= pdf_y <= y1:
                page.add_highlight_annot(fitz.Rect(x0, y0, x1, y1))
                self.show_page()
                print("highlighted word:", text)
                return

        print("No word here")

    def click_cursor(self):
        """Report the canvas item closest to the virtual cursor."""
        item = self.canvas.find_closest(self.cursor_x, self.cursor_y)
        print(f"Clicked on item: {item}")

    def move_cursor(self, hand):
        """Move the virtual cursor from a hand landmark (legacy helper)."""
        self.move_cursor_to(hand[8].x, hand[8].y)

    def move_cursor_from_face(self, face):
        """Move the cursor from the face's nose-tip position."""
        nose_tip = face[HeadCursorController.NOSE_TIP_INDEX]
        self.move_cursor_to(nose_tip.x, nose_tip.y)

    def move_cursor_to(self, normalized_x, normalized_y):
        """Move the virtual cursor to normalized camera coordinates."""
        target_x = normalized_x * self.canvas.winfo_width()
        target_y = normalized_y * self.canvas.winfo_height()

        self.cursor_x += (target_x - self.cursor_x) * self.cursor_smoothing
        self.cursor_y += (target_y - self.cursor_y) * self.cursor_smoothing
        self.cursor_x = int(self.cursor_x)
        self.cursor_y = int(self.cursor_y)

        self.draw_cursor()

    def move_cursor_by(self, normalized_x, normalized_y):
        """Move the cursor by relative, normalized camera movement."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.cursor_x = int(max(0, min(width, self.cursor_x + normalized_x * width)))
        self.cursor_y = int(max(0, min(height, self.cursor_y + normalized_y * height)))

        self.draw_cursor()

    def draw_cursor(self):
        """Redraw the virtual cursor at its current location."""
        if self.cursor_id is not None:
            self.canvas.coords(
                self.cursor_id,
                self.cursor_x - 5,
                self.cursor_y - 5,
                self.cursor_x + 5,
                self.cursor_y + 5,
            )

    def update_camera(self):
        """Process a camera frame when an external caller requests one."""
        self.camera.update()

    def scroll(self, amount):
        self.canvas.yview_scroll(amount, "units")

    def on_mousewheel(self, event):
        if event.num == 4:
            self.scroll(-3)
        elif event.num == 5:
            self.scroll(3)
        else:
            self.scroll(int(-event.delta / 120))

    def on_resize(self, _event):
        if self.doc:
            self.show_page()

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        if path:
            self.pdf_path = path
            self.doc = fitz.open(path)
            self.page_num = 0
            self.show_page()

    def show_page(self):
        """Render the current PDF page."""
        if not self.doc:
            return

        self.canvas.delete("all")
        self.photos = []

        page = self.doc[self.page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        photo = ImageTk.PhotoImage(image)
        self.photos.append(photo)

        x = max(20, (self.canvas.winfo_width() - pix.width) // 2)
        y = 20
        self.pdf_x_screen = x
        self.pdf_y_screen = y

        self.canvas.create_image(x, y, anchor="nw", image=photo)
        if self.ENABLE_CURSOR_CONTROL:
            self.cursor_id = self.canvas.create_oval(
                self.cursor_x - 5,
                self.cursor_y - 5,
                self.cursor_x + 5,
                self.cursor_y + 5,
                fill="red",
                outline="white",
                width=2,
            )
            self.canvas.tag_raise(self.cursor_id)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def next_page(self):
        if self.doc and self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.show_page()

    def previous_page(self):
        if self.doc and self.page_num > 0:
            self.page_num -= 1
            self.show_page()

    def zoom_in(self):
        self.zoom_by(0.2)

    def zoom_out(self):
        self.zoom_by(-0.2)

    def zoom_by(self, amount):
        """Apply a smooth, movement-driven zoom amount."""
        new_zoom = max(0.4, min(4.0, self.zoom + amount))
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            self.show_page()

    def close(self):
        """Save highlights and release application resources."""
        if self.doc:
            try:
                output_path = "MagicRead_highlighted.pdf"
                self.doc.save(output_path, garbage=4, deflate=True)
                print(f"Saved highlighted PDF: {output_path}")
            except Exception as error:
                print("Error saving PDF:", error)

        self.camera.close()
        self.root.destroy()
