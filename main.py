import cv2
import dehazing_algorithm as alg
import time
import os
import sys
from tkinter import *
from tkinter import Tk, Canvas, PhotoImage, Label, Button, Toplevel, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from tkinter import font as tkFont

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath('.')

class App:
    bgi = None
    open_window_count = 0
    
    def __init__(self, master):
        self.font = tkFont.Font(family='Courier', weight="bold")
        App.open_window_count += 1
        self.master = master
        self.master.title("Dehazing App")
        try:
            self.master.iconbitmap("assets/icon.ico")
        except Exception as e:
            pass
            
        self.master.state('zoomed')
        try:
            App.bgi = PhotoImage(file="assets/background.png")
            background_image = App.bgi
            self.background_canvas = Canvas(self.master, width=background_image.width(), height=background_image.height())
            self.background_canvas.grid(row=0, column=0, sticky="nsew")
            self.background_canvas.create_image(0, 0, anchor=NW, image=background_image)
        except Exception as e:
            pass


        welcome_label = Label(self.master, text="Welcome to Dehazing System", font=(self.font, 24),bg="white")
        welcome_label.grid(row=1, column=0, pady=20,sticky="nsew")

        self.upload_image_button = Button(self.master, text="Upload Image", command=self.upload_image)
        self.upload_video_button = Button(self.master, text="Upload Video", command=self.upload_video)
        self.start_realtime_button = Button(self.master, text="Start Realtime Dehazing", command=self.select_realtime_source)
        self.upload_image_button.grid(row=2, column=0, pady=10,sticky="nsew")
        self.upload_video_button.grid(row=3, column=0, pady=10,sticky="nsew")
        self.start_realtime_button.grid(row=4, column=0, pady=10,sticky="nsew")

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def on_close(self):       
        App.open_window_count -= 1
        self.master.destroy()
        if App.open_window_count == 0:
            root.quit()

    def create_option_window(self, option):
        App.open_window_count += 1
        self.option_window = Toplevel()
        try:
            self.option_window.iconbitmap("assets/icon.ico")
        except Exception as e:
            pass
        
        self.option_window.title(f"Option: {option}")
        self.option_window.configure(bg="white")
        back_button = Button(self.option_window, text="Back to Homepage", command=self.back_to_homepage)
        back_button.pack(pady=10)
    
    def back_to_homepage(self):
        if self.option_window:
            self.option_window.destroy()
            App.open_window_count -= 1
        
    def upload_image(self):
        self.create_option_window("Upload Image")
        upload_image_label = Label(self.option_window, text="Upload Image to be Dehazed", font=(self.font, 18),bg="white")
        upload_image_label.pack(pady=10)
        upload_button = Button(self.option_window, text="Upload Image", command=self.choose_image)
        upload_button.pack(pady=10)

    def choose_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            original_image = cv2.imread(file_path)
            original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            original_image = Image.fromarray(original_image)
            original_photo = ImageTk.PhotoImage(original_image)
            cap = cv2.imread(file_path)
            cap = cv2.cvtColor(cap, cv2.COLOR_BGR2RGB)
            start_time=time.time()
            output=alg.dehaze_frame(cap,4,8)*255
            end_time=time.time()
            output=output.astype(np.uint8)

            
            total_time=end_time-start_time
            dehazed_photo = ImageTk.PhotoImage(Image.fromarray(output))

        screen_width = self.option_window.winfo_screenwidth()
        screen_height = self.option_window.winfo_screenheight()

        if hasattr(self, 'original_canvas'):
            self.original_canvas.destroy()

        self.original_canvas = Canvas(self.option_window, width=screen_width // 2, height=screen_height,bg="white")
        self.original_canvas.pack(side="left", fill="both", expand=True)

        self.original_canvas.create_image(0, 0, anchor="nw", image=original_photo)
        self.original_canvas.image = original_photo

        original_label = Label(self.option_window, text="Original Image",bg="white")
        original_label.place(x=screen_width // 7, y=screen_height // 5)

        if hasattr(self, 'dehazed_canvas'):
            self.dehazed_canvas.destroy()

        self.dehazed_canvas = Canvas(self.option_window, width=screen_width // 2, height=screen_height,bg="white")
        self.dehazed_canvas.pack(side="right", fill="both", expand=True)
        self.dehazed_canvas.create_image(0, 0, anchor="nw", image=dehazed_photo)
        self.dehazed_canvas.image = dehazed_photo
    
        dehazed_label = Label(self.option_window, text="Dehazed Image",bg="white")
        dehazed_label.place(x=5 * screen_width // 7, y=screen_height // 5)

        label_button_frame = Frame(self.option_window, bg="white")
        label_button_frame.pack(pady=10)

        time_label = Label(label_button_frame, text=f"Time taken to dehaze: {total_time} milliseconds",bg="white")
        time_label.grid(row=0, column=0, pady=(0, 10))

        download_button = Button(label_button_frame, text="Download Dehazed Image", command=lambda: self.download_dehazed(output))
        download_button.grid(row=1, column=0, pady=(0, 10))

        label_button_frame.place(relx=0.5, rely=0.9, anchor="center")
        self.option_window.attributes("-topmost", True)
    def download_dehazed(self, dehazed_image):
        self.option_window.attributes("-topmost", False)
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])

        if file_path:
            Image.fromarray(dehazed_image).save(file_path)
            messagebox.showinfo("Download Completed", f"Dehazed image saved at: {file_path}")
    upload_button=None
    t=None
    def upload_video(self):
        self.create_option_window("Upload Video")
        upload_video_label = Label(self.option_window, text="Upload Video to be Dehazed", font=(self.font, 18),bg="white")
        upload_video_label.pack(pady=10)

        self.upload_button = Button(self.option_window, text="Upload Video", command=self.choose_video)
        self.upload_button.pack(pady=10)
        self.t = Label(self.option_window, text=f"Press Q to stop previewing dehazed video")

    def choose_video(self):
        file_path = filedialog.askopenfilename(title="Select a Video", filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
        button_frame = Frame(self.option_window,bg="white")
        button_frame.pack(pady=10)
        
        self.option_window.attributes("-topmost", True)
        self.upload_button.pack_forget()
        self.t.pack(pady=10)
        def preview():

            if file_path:
                # extract frames from video
                capture = cv2.VideoCapture(file_path) #change here for input location
                #REALTIME DEHAZING
                skip=1
                while True:
                    for i in range(skip):
                        success, frame = capture.read()
                        if not success:
                            cv2.destroyAllWindows()
                            break
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                        break
                    dehazed_frame = alg.dehaze_frame(frame, 5, n=8)
                    cv2.imshow('dehazed',dehazed_frame)

            capture.release()
        def download():
            output_path = filedialog.asksaveasfilename(defaultextension="*.avi", filetypes=[("avi Files", "*.avi")])
            if not output_path or output_path=='':
                return
            capture = cv2.VideoCapture(file_path)
            fps = int(capture.get(cv2.CAP_PROP_FPS))
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            #Create Video writer for the dehazed video
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            while True:
                for i in range(1):
                    success, frame = capture.read()
                if not success:
                    break
                dehazed_frame = alg.dehaze_frame(frame, 5, n=8) * 255
                dehazed_frame = dehazed_frame.astype(np.uint8)
                out.write(dehazed_frame)
            messagebox.showinfo("Download Completed", f"Dehazed video saved at: {output_path}")
            capture.release()
            out.release()
        preview_button = Button(button_frame, text="Preview Dehazed Video", command=preview)
        preview_button.pack(side="left", padx=10)
        download_button = Button(button_frame, text="Download Dehazed Video", command=download)
        download_button.pack(side="left", padx=10)     

    sources=[]
    def select_realtime_source(self):
        self.create_option_window("Select Input Source")
        self.selected_source = StringVar()
        self.selected_source.set("Camera")  #Set default value
        title_label = Label(self.option_window, text="Select Input Source", font=(self.font, 18),bg="white")
        title_label.pack(pady=10)
        sources = ["Camera", "USB Camera1","USB Camera2", "IP Webcam"]
        self.sources=sources
        # Drop-down menu for selecting the input source
        source_menu = OptionMenu(self.option_window, self.selected_source, *sources)
        source_menu.pack(pady=10)
        self.selected_source.set("Camera")
        q = Label(self.option_window, text=f"Press Q to stop real-time dehazing",bg="white")
        q.pack(pady=10)
        start_button = Button(self.option_window, text="Start Realtime Dehazing", command=self.set_param)
        start_button.pack(pady=10)
        self.image_path = None
        
    param=None

    def set_param(self):
        selected_option = self.selected_source.get()
        if(selected_option==self.sources[-1]):
            ip_webcam_window = Toplevel(self.option_window)
            ip_webcam_window.title("Enter IP Webcam URL")
            try:
                ip_webcam_window.iconbitmap("assets/icon.ico")
            except Exception as e:
                pass
            url_label = Label(ip_webcam_window, text="Enter IP Webcam URL:",bg="white")
            url_label.pack(pady=10)
            example = Label(ip_webcam_window, text="Your URL might look like : http://ip:port, https://ip:port, rtsp://ip:port/h264_ulaw.sdp or rtsp://ip:port/h264_pcm.sdp",bg="white")
            example.pack(pady=20)
            url_entry = Entry(ip_webcam_window,width=40)
            url_entry.pack(pady=10)
            submit_button = Button(ip_webcam_window, text="Submit", command=lambda: self.start_realtime_dehazing(url_entry.get()))
            submit_button.pack(pady=10)
        else:
            self.param=self.sources.index(selected_option)
            self.start_realtime_dehazing()

    def start_realtime_dehazing(self,url=None):
        if url:
            self.param = url
        capture=cv2.VideoCapture(self.param)
        if not capture.isOpened():
            messagebox.showinfo("Error: Could not open Video Stream", f"Try a different URL! Consider changing protocol (rtsp/http) or changing ip or port address.")
            return
        skip_frames=1
        while(True):
            frame=None
            for i in range(skip_frames):
                success, frame = capture.read()
                if not success:
                    break
            cv2.imshow('original frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            dehazed_frame = alg.dehaze_frame(frame, 5, n=8)
            cv2.imshow('dehazed',dehazed_frame)
        capture.release()

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.config(bg="white")
    
    try:
        root.iconbitmap("assets/icon.ico")
    except Exception as e:
        pass
    root.mainloop()