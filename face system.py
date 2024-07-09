import os
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import sqlite3

class FaceDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Detection")
        self.scan_root = None

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        self.captured_img_dir = "captured_img"
        if not os.path.exists(self.captured_img_dir):
            os.makedirs(self.captured_img_dir)

        self.student_id = ""
        self.first_name = ""
        self.last_name = ""

        self.update_frame()

        description_label = tk.Label(self.root, text="Welcome! If you haven't registered yet, just click the 'REGISTER' button below.",
                                     font=("Calibri", 12), fg="black")
        description_label.pack(pady=10)

        register_button = ttk.Button(self.root, text="REGISTER", command=self.register_button_click)
        register_button.pack()

       
        self.conn = sqlite3.connect("face_system.db")
        self.cursor = self.conn.cursor()

       
        self.create_users_table()

    def create_users_table(self):
   
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                student_id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                face_image_path BLOB UNIQUE
            )
        ''')
        self.conn.commit()

    def store_user_info(self, student_id, first_name, last_name, face_image_path):
        try:
            self.cursor.execute("INSERT INTO users (student_id, first_name, last_name, face_image_path) VALUES (?, ?, ?, ?)",
                                (student_id, first_name, last_name, face_image_path))
            self.conn.commit()
        except sqlite3.IntegrityError:
           
            print("User with the same face_image_path already exists.")
            self.conn.rollback()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            outsider_detected = True  

            
            for filename in os.listdir(self.captured_img_dir):
                if filename.endswith(".jpg"):
                    captured_img_path = os.path.join(self.captured_img_dir, filename)
                    captured_img = cv2.imread(captured_img_path)

                    
                    for (x, y, w, h) in faces:
                        face = frame[y:y + h, x:x + w]
                        match, name = self.compare_faces(face, captured_img, self.student_id, self.first_name, self.last_name)
                        if match:
                            cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            outsider_detected = False  

            if outsider_detected:
             
                for (x, y, w, h) in faces:
                    cv2.putText(frame, "Outsider", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            self.video_label.img = img_tk
            self.video_label.config(image=img_tk)
        self.root.after(10, self.update_frame)

    def compare_faces(self, face1, face2, student_id, first_name, last_name):
       
        if face1 is None or face2 is None:
            return False, None


        face1 = cv2.resize(face1, (face2.shape[1], face2.shape[0]))
 
        diff = cv2.absdiff(face1, face2)

       
        mse = np.mean(diff)

       
        threshold = 100

       
        if mse < threshold:
            return True, f"CJC-INSIDER-{first_name} {last_name}"
        else:
            return False, None

    def register_button_click(self):
        self.root.withdraw()
        self.register_window()

    def register_window(self):
        register_root = tk.Toplevel()
        register_root.title("Registration")

        description_label = tk.Label(register_root, text="COMPLETE THE FORM:", font=("Calibri", 25))
        description_label.pack(pady=10)

        student_id_label = tk.Label(register_root, text="Student ID:", font=("Calibri", 18))
        student_id_label.pack()
        student_id_entry = ttk.Entry(register_root, font=("Calibri", 18))
        student_id_entry.pack()

        first_name_label = tk.Label(register_root, text="First Name:", font=("Calibri", 18))
        first_name_label.pack()
        first_name_entry = ttk.Entry(register_root, font=("Calibri", 18))
        first_name_entry.pack()

        last_name_label = tk.Label(register_root, text="Last Name:", font=("Calibri", 18))
        last_name_label.pack()
        last_name_entry = ttk.Entry(register_root, font=("Calibri", 18))
        last_name_entry.pack()

        def next_button_click():
            self.student_id = student_id_entry.get()
            self.first_name = first_name_entry.get()
            self.last_name = last_name_entry.get()
            if self.student_id and self.first_name and self.last_name:
                register_root.destroy()
                self.camera_window()

        next_button = ttk.Button(register_root, text="NEXT", command=next_button_click)
        next_button.pack()

    def camera_window(self):
        self.camera_root = tk.Toplevel(self.root)
        self.camera_root.title("Camera")

        capture_label = tk.Label(self.camera_root, text="Position your face in the camera frame and click the capture button.", font=("Calibri", 16))
        capture_label.pack(pady=10)

        self.camera_label = tk.Label(self.camera_root)
        self.camera_label.pack()

        self.capture_button = ttk.Button(self.camera_root, text="CAPTURE", command=self.capture_image)
        self.capture_button.pack()

        self.submit_button = ttk.Button(self.camera_root, text="SUBMIT", command=self.submit_image)
        self.submit_button.pack()
        self.submit_button.config(state=tk.DISABLED)

        self.retake_button = ttk.Button(self.camera_root, text="RETAKE", command=self.retake_image)
        self.retake_button.pack()
        self.retake_button.config(state=tk.DISABLED)

        self.capture_label = tk.Label(self.camera_root)
        self.capture_label.pack()

        self.update_camera_feed()

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            for (x, y, w, h) in faces:
                face = frame[y:y + h, x:x + w]
                filename = os.path.join(self.captured_img_dir, f"{self.student_id} - {self.first_name} {self.last_name}.jpg")
                cv2.imwrite(filename, face)
                self.update_capture_label(face)
                self.submit_button.config(state=tk.NORMAL)
                self.retake_button.config(state=tk.NORMAL)
                self.capture_button.config(state=tk.DISABLED)

    def submit_image(self):
        self.submit_button.config(state=tk.DISABLED)
        self.retake_button.config(state=tk.DISABLED)
        self.capture_button.config(state=tk.DISABLED)

        # Close the camera window
        self.camera_root.destroy()

        # Store the information in the database
        if self.student_id and self.first_name and self.last_name:
            filename = f"{self.student_id} - {self.first_name} {self.last_name}.jpg"
            image_path = os.path.join(self.captured_img_dir, filename)
            self.store_user_info(self.student_id, self.first_name, self.last_name, image_path)

        # Open the SCAN window
        self.scan_window()

    def retake_image(self):
        self.submit_button.config(state=tk.DISABLED)
        self.retake_button.config(state=tk.DISABLED)
        self.capture_button.config(state=tk.NORMAL)
        self.capture_label.config(image=None)

    def update_capture_label(self, face_image):
        captured_img = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
        captured_img = captured_img.resize((100, 100), Image.LANCZOS)
        captured_img_tk = ImageTk.PhotoImage(captured_img)
        self.capture_label.config(image=captured_img_tk)
        self.capture_label.image = captured_img_tk

    def update_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            self.camera_label.img = img_tk
            self.camera_label.config(image=img_tk)
        self.camera_label.after(10, self.update_camera_feed)

    def scan_window(self):
        self.scan_root = tk.Toplevel(self.root)
        self.scan_root.title("SCAN")

        scan_label = tk.Label(self.scan_root, text="Your input is greatly appreciated. Thank you!", font=("Calibri", 30))
        scan_label.pack(pady=20)

        scan_button = ttk.Button(self.scan_root, text="Scan", command=self.start_scan)
        scan_button.pack(pady=10)

    def start_scan(self):
        
 
        self.scan_root.destroy()

       
        self.root.deiconify()

    def run(self):
        self.root.mainloop()
        self.cap.release()
        cv2.destroyAllWindows()
        self.conn.close()  

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceDetectionApp(root)
    app.run()