"""--------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
 ▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄  ▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄  ▄▄▄       ▄▄▄  ▄▄▄  ▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄     
 █▄▄▄▄▄▄█   █▄▄▄▄▄█  ██▄▄▄▄▄▄  ███  ██▄▄▄▄██ ███  ███       ███  ███  ██▄▄▄▄▄  ██▄▄▄▄▄     
 ██   ██   ██   ██  ██        ███  ██    ██ ███  ███       ███  ███  ██       ██          
 ██▄▄▄▄▄█   ██▄▄▄▄█  ██▄▄▄▄   ███  ██    ██ ███  ███       ███  ███  ██▄▄▄▄▄  ██          
 ██▀▀▀▀    ██▀▀▀▀█   ▀▀▀▀▀██  ███  ██    ██ ███  ███       ███  ███   ▀▀▀▀▀██ ██          
 ██        ██   ██        ██  ███  ██    ██ ███  ███       ███  ███        ██ ██          
 ██        ██   ██  ██▄▄▄▄██  ███  ██▄▄▄▄██ ████████       ████████  ██▄▄▄▄██ ██▄▄▄▄▄     
 ▀▀        ▀▀   ▀▀   ▀▀▀▀▀▀   ▀▀▀  ▀▀▀▀▀▀▀   ▀▀▀▀▀          ▀▀▀▀▀    ▀▀▀▀▀▀   ▀▀▀▀▀▀▀      
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------"""

import os
import json
import platform
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Core media processors
from moviepy.audio.io.AudioFileClip import AudioFileClip
import soundfile as sf

class UniversalSoundConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Paths for theme settings storage
        self.config_dir = os.path.join(os.path.expanduser("~"), ".universal_sound_converter")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Load theme setting memory state
        self.saved_theme = self.load_theme_preference()

        # Window configuration
        self.title("Universal Sound Converter")
        self.geometry("620x560")
        self.resizable(False, False)

        # Apply the saved appearance mode
        ctk.set_appearance_mode(self.saved_theme)
        ctk.set_default_color_theme("blue")

        # App operational variables
        self.input_files = []  
        self.supported_inputs = ["MP4", "WAV", "FLAC", "M4A", "MP3"]
        self.supported_outputs = ["MP3", "WAV", "FLAC"]

        # GUI State Tracking Variables
        self.input_format_var = ctk.StringVar(value="MP4")
        self.output_format_var = ctk.StringVar(value="MP3")
        self.theme_menu_var = ctk.StringVar(value=self.saved_theme)

        # Create user interface elements
        self.create_widgets()

    def load_theme_preference(self):
        """Loads the preferred user theme setting from local JSON memory store."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    theme = data.get("theme_mode", "Dark")
                    if theme in ["System", "Dark", "Light"]:
                        return theme
        except Exception:
            pass
        return "Dark"  # Default initial selection fallback state

    def save_theme_preference(self, theme_choice):
        """Saves a modified theme selection persistently to the local JSON configuration file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump({"theme_mode": theme_choice}, f)
        except Exception as e:
            print(f"Failed to record setting update configuration: {e}")

    def create_widgets(self):
        # Window Heading Title Label
        self.title_label = ctk.CTkLabel(
            self, text="Universal Sound Converter", font=ctk.CTkFont(size=26, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))

        # Advanced Theme Controller Selector Layout Row Frame
        self.theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.theme_frame.pack(anchor="ne", padx=30, pady=(0, 5))
        
        self.theme_menu_label = ctk.CTkLabel(self.theme_frame, text="Appearance Mode:", font=ctk.CTkFont(size=11))
        self.theme_menu_label.pack(side="left", padx=5)

        self.theme_option_menu = ctk.CTkOptionMenu(
            self.theme_frame, 
            values=["System", "Dark", "Light"], 
            variable=self.theme_menu_var,
            command=self.change_theme_event,
            width=100,
            height=24
        )
        self.theme_option_menu.pack(side="right", padx=5)

        # File Discovery Selection Frame Block Container
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=30, fill="x")

        self.file_label = ctk.CTkLabel(
            self.file_frame, text="No media files selected...", text_color="gray", width=400, anchor="w"
        )
        self.file_label.pack(side="left", padx=15, pady=15)

        self.browse_btn = ctk.CTkButton(
            self.file_frame, text="Browse Files", command=self.browse_files, width=120
        )
        self.browse_btn.pack(side="right", padx=15, pady=15)

        # Dual Dynamic Directional Matrix Settings Configuration Block
        self.matrix_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.matrix_frame.pack(pady=15, padx=30, fill="x")

        # Source Format Dropdown Selector Input
        self.from_label = ctk.CTkLabel(self.matrix_frame, text="Input Format:", font=ctk.CTkFont(size=13, weight="bold"))
        self.from_label.grid(row=0, column=0, padx=20, pady=5, sticky="w")
        
        self.input_options = ctk.CTkComboBox(
            self.matrix_frame, values=self.supported_inputs, variable=self.input_format_var, width=180, command=self.reset_file_list
        )
        self.input_options.grid(row=1, column=0, padx=20, pady=5)

        # Spatial Transition Spacer Arrow Graphic
        self.arrow_label = ctk.CTkLabel(self.matrix_frame, text="➡️", font=ctk.CTkFont(size=20))
        self.arrow_label.grid(row=1, column=1, padx=10, pady=5)

        # Destination Output Format Dropdown Selector Target
        self.to_label = ctk.CTkLabel(self.matrix_frame, text="Output Format:", font=ctk.CTkFont(size=13, weight="bold"))
        self.to_label.grid(row=0, column=2, padx=20, pady=5, sticky="w")
        
        self.output_options = ctk.CTkComboBox(
            self.matrix_frame, values=self.supported_outputs, variable=self.output_format_var, width=180
        )
        self.output_options.grid(row=1, column=2, padx=20, pady=5)

        # Active Feedback Progress Operational Status Label Tracker
        self.status_label = ctk.CTkLabel(self, text="Status: Idle", text_color="gray", font=ctk.CTkFont(size=13))
        self.status_label.pack(pady=(20, 5))

        # Horizontal Graph Visual Loading Operational Linear Tracking Element
        self.progress_bar = ctk.CTkProgressBar(self, width=440)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        # Primary Submission Process Activation Execution Button
        self.convert_btn = ctk.CTkButton(
            self, text="Convert", command=self.start_conversion_thread, 
            fg_color="#1f6aa5", hover_color="#144870", width=220, height=40, font=ctk.CTkFont(size=15, weight="bold")
        )
        self.convert_btn.pack(pady=25)

    def change_theme_event(self, selected_mode):
        """Updates runtime layout display values and modifies stored memory objects accordingly."""
        ctk.set_appearance_mode(selected_mode)
        self.save_theme_preference(selected_mode)

    def reset_file_list(self, choice):
        self.input_files = []
        self.file_label.configure(text="No media files selected...", text_color="gray")

    def browse_files(self):
        target_ext = self.input_format_var.get().lower()
        filter_label = f"{target_ext.upper()} Media Files"
        
        file_types = [(filter_label, f"*.{target_ext}"), ("All Files", "*.*")]
        selected_paths = filedialog.askopenfilenames(title=f"Universal Sound Converter - Select .{target_ext.upper()}", filetypes=file_types)
        
        if selected_paths:
            self.input_files = list(selected_paths)
            count = len(self.input_files)
            if count == 1:
                filename = os.path.basename(self.input_files[0])
                self.file_label.configure(text=filename, text_color=("#1a1a1a", "white"))
            else:
                self.file_label.configure(text=f"{count} files staged for processing", text_color=("#1a1a1a", "white"))

    def start_conversion_thread(self):
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select source media tracks first!")
            return

        input_fmt = self.input_format_var.get()
        output_fmt = self.output_format_var.get()

        if input_fmt == output_fmt:
            messagebox.showwarning("Warning", "Input format and output format are identical!")
            return

        self.convert_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.input_options.configure(state="disabled")
        self.output_options.configure(state="disabled")
        self.theme_option_menu.configure(state="disabled")
        self.progress_bar.set(0)
        
        threading.Thread(target=self.process_batch_matrix, daemon=True).start()

    def get_unique_filename(self, target_path):
        base, ext = os.path.splitext(target_path)
        counter = 1
        unique_path = target_path
        while os.path.exists(unique_path):
            unique_path = f"{base} ({counter}){ext}"
            counter += 1
        return unique_path

    def open_destination_folder(self, file_path):
        folder_path = os.path.dirname(file_path)
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", folder_path])
            else:
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory: {e}")

    def convert_engine_router(self, file_path, target_ext, output_path):
        if target_ext == "mp3":
            clip = AudioFileClip(file_path)
            clip.write_audiofile(output_path, logger=None)
            clip.close()
        else:
            clip = AudioFileClip(file_path)
            fps = clip.fps if clip.fps else 44100
            audio_array = clip.to_soundarray(fps=fps)
            clip.close()
            sf.write(output_path, audio_array, fps, format=target_ext.upper())

    def process_batch_matrix(self):
        total_files = len(self.input_files)
        success_count = 0
        last_saved_path = ""
        target_ext = self.output_format_var.get().lower()

        for idx, file_path in enumerate(self.input_files):
            try:
                filename = os.path.basename(file_path)
                self.status_label.configure(text=f"Processing ({idx + 1}/{total_files}): {filename}", text_color="#1f6aa5")
                
                base, _ = os.path.splitext(file_path)
                intended_output_path = f"{base}.{target_ext}"
                output_file_path = self.get_unique_filename(intended_output_path)
                last_saved_path = output_file_path
                
                self.convert_engine_router(file_path, target_ext, output_file_path)
                success_count += 1
                
            except Exception as e:
                print(f"Error converting asset {file_path}: {e}")
                
            progress_value = (idx + 1) / total_files
            self.progress_bar.set(progress_value)

        self.status_label.configure(text="Universal Sound Converter pipeline complete!", text_color="green")
        
        if success_count > 0:
            open_folder = messagebox.askyesno(
                "Conversion Complete",
                f"Successfully formatted {success_count}/{total_files} file(s) to {target_ext.upper()}!\n\nOpen destination folder?"
            )
            if open_folder and last_saved_path:
                self.open_destination_folder(last_saved_path)
        else:
            messagebox.showerror("Error", "All audio matrix mutations failed.")

        # Reactivate user control element states
        self.convert_btn.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self.input_options.configure(state="normal")
        self.output_options.configure(state="normal")
        self.theme_option_menu.configure(state="normal")
        self.input_files = []
        self.file_label.configure(text="No media files selected...", text_color="gray")

if __name__ == "__main__":
    app = UniversalSoundConverterApp()
    app.mainloop()
