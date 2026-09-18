import tkinter as tk

from pdf_viewer import PDFViewer


def main():
    root = tk.Tk()
    root.geometry("1000x700")

    viewer = PDFViewer(root)
    root.protocol("WM_DELETE_WINDOW", viewer.close)
    root.mainloop()


if __name__ == "__main__":
    main()
