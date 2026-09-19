# MagicRead

MagicRead is an experimental project where I explored **controlling a PDF viewer using hand gestures**.

The main goal of this project was not to build a complete PDF reader, but to understand how gesture-controlled interfaces work and how computer vision can be used to control applications without traditional mouse or keyboard input.

## What I Built

Using a webcam and MediaPipe hand tracking, I implemented gesture-based controls for a PDF viewer.

The project currently supports:

* Open and display PDF files
* Scroll through pages using hand gestures
* Move between pages using hand gestures
* Zoom in and out using two hands
* Move a cursor using hand tracking
* Select and highlight words using gestures

## Technologies Used

* **Python** — Main programming language
* **OpenCV** — Webcam input and image processing
* **MediaPipe** — Hand landmark detection and gesture tracking
* **PyMuPDF** — PDF rendering and text/annotation handling
* **Tkinter** — Graphical user interface
* **Pillow** — Converting rendered PDF pages for display

## Project Structure

```text
magicRead/
├── main.py
├── pdf_viewer.py
├── camera_controller.py
├── gesture_controller.py
├── gestures.py
├── face_controller.py
├── hand_landmarker.task
├── face_landmarker.task
└── requirements.txt
```

## Why I Built This

I started this project after seeing videos and reels where people interact with maps and other interfaces using hand movements.

Instead of directly trying to reproduce those systems, I wanted to understand the underlying idea myself:

```text
Camera
   ↓
Hand Detection
   ↓
Hand Landmarks
   ↓
Gesture Recognition
   ↓
Application Control
```

Building MagicRead helped me experiment with this interaction pipeline and understand some of the practical challenges involved, such as gesture ambiguity, tracking stability, cursor jitter, and controlling a GUI using computer vision.

## Project Status

This project is **complete as a learning experiment**.

I am not planning to turn MagicRead into a full-featured PDF reader. The purpose was to explore gesture-based computer interaction and understand how systems like the ones seen in demos and videos can be built.

## What I Learned

Through this project I learned about:

* Hand landmark detection
* Gesture recognition
* Working with MediaPipe
* Real-time webcam processing
* Mapping normalized hand coordinates to screen coordinates
* PDF rendering with PyMuPDF
* GUI development with Tkinter
* Handling real-time input and gesture stability
* Separating camera, gesture, and application logic

## Future Experiments

The next step is not to add more PDF features, but to apply the same ideas to other interfaces such as **maps and spatial navigation**, where gesture-based interaction can be more natural and interesting.

---

**MagicRead — a small experiment in gesture-controlled interfaces.**
