import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw # Ensure Pillow is installed: pip install Pillow
import random
import time
import threading
import queue
import os

class FSMDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ARCHON Hazard Monitoring Dashboard")
        self.geometry("1000x700")
        self.configure(bg="#2c3e50") # Dark blue-grey background

        # Suppress the Tk deprecation warning on macOS
        os.environ['TK_SILENCE_DEPRECATION'] = '1'

        # Clear the log file on startup to ensure fresh start
        self.log_filename = "fsm_log.txt"
        self.clear_log_file()

        # --- Dashboard Title ---
        self.title_label = tk.Label(self, text="ARCHON Hazard Monitoring",
                                    font=("Inter", 28, "bold"), fg="#ecf0f1", bg="#2c3e50", pady=15)
        self.title_label.pack(pady=(20, 10))

        # --- Main Frame for Panels ---
        main_frame = ttk.Frame(self, padding="20 20 20 20", style="Dark.TFrame")
        main_frame.pack(expand=True, fill="both")

        # Configure global ttk style for dark theme
        self.style = ttk.Style()
        self.style.theme_use("clam") # "clam" is a good base for customization

        self.style.configure("Dark.TFrame", background="#34495e", borderwidth=5, relief="flat", bordercolor="#2c3e50")
        self.style.configure("Dark.TLabel", background="#34495e", foreground="#ecf0f1", font=("Inter", 12))
        self.style.configure("Big.Dark.TLabel", background="#34495e", foreground="#ecf0f1", font=("Inter", 18, "bold"))
        self.style.configure("Red.TLabel", background="#e74c3c", foreground="white", font=("Inter", 18, "bold")) # FLUSH/LOCK
        self.style.configure("Orange.TLabel", background="#f39c12", foreground="white", font=("Inter", 18, "bold")) # STALL
        self.style.configure("Green.TLabel", background="#27ae60", foreground="white", font=("Inter", 18, "bold")) # OK
        self.style.configure("Info.TLabel", background="#34495e", foreground="#95a5a5", font=("Inter", 10, "italic")) # Smaller info text
        
        # --- Progressbar Styles (Simplified for macOS Tk compatibility) ---
        # We will use the default "TProgressbar" style and just dynamically map its colors.

        # Configure the *default* TProgressbar style's visual properties
        self.style.configure("TProgressbar", thickness=20, troughcolor="#7f8c8d", borderwidth=0)

        # Initial mapping for Entropy Meter (horizontal)
        self.style.map("TProgressbar", background=[
            ('!disabled', '#2ecc71'), # Default green for horizontal
            ('active', '#2ecc71')
        ])

        # Initial mapping for Prediction Meter (vertical)
        self.style.configure("Vertical.TProgressbar", thickness=20, troughcolor="#7f8c8d", borderwidth=0)
        self.style.map("Vertical.TProgressbar", background=[
            ('!disabled', '#3498db'), # Default blue for vertical
            ('active', '#3498db')
        ])

        # --- Panel 1: FSM State Indicator ---
        fsm_frame = ttk.LabelFrame(main_frame, text="FSM State", style="Dark.TFrame", padding="10")
        fsm_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.fsm_state_label = ttk.Label(fsm_frame, text="Waiting for data...", style="Green.TLabel", anchor="center")
        self.fsm_state_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.cycle_label = ttk.Label(fsm_frame, text="Cycle: Waiting...", style="Info.TLabel")
        self.cycle_label.pack(pady=(5, 0))

        # --- Panel 2: Entropy Score ---
        entropy_frame = ttk.LabelFrame(main_frame, text="Entropy Score", style="Dark.TFrame", padding="10")
        entropy_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.entropy_value_label = ttk.Label(entropy_frame, text="Waiting...", style="Big.Dark.TLabel", anchor="center")
        self.entropy_value_label.pack(pady=(10, 5))

        # Use the default TProgressbar style for horizontal.
        self.entropy_meter = ttk.Progressbar(entropy_frame, orient="horizontal", length=200, mode="determinate", style="TProgressbar")
        self.entropy_meter.pack(padx=10, pady=5, fill="x")
        self.entropy_meter["maximum"] = 255 # 8-bit entropy score

        self.entropy_status_label = ttk.Label(entropy_frame, text="Waiting for data...", style="Info.TLabel")
        self.entropy_status_label.pack(pady=(5, 0))

        # --- Panel 3: Override Source Indicator ---
        override_frame = ttk.LabelFrame(main_frame, text="Override Source", style="Dark.TFrame", padding="10")
        override_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.override_source_label = ttk.Label(override_frame, text="Waiting...", style="Big.Dark.TLabel", anchor="center")
        self.override_source_label.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Panel 4: Waveform Snapshot Viewer (Placeholder) ---
        waveform_frame = ttk.LabelFrame(main_frame, text="Waveform Snapshot", style="Dark.TFrame", padding="10")
        waveform_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        try:
            # Create a simple placeholder image dynamically
            img = Image.new('RGB', (200, 150), color = 'darkgray')
            d = ImageDraw.Draw(img)
            d.text((50,60), "Waveform Plot Placeholder", fill=(0,0,0))
            self.waveform_img = ImageTk.PhotoImage(img)
            self.waveform_label = tk.Label(waveform_frame, image=self.waveform_img, bg="#34495e")
            self.waveform_label.pack(expand=True, fill="both", padx=5, pady=5)
        except Exception as e:
            # Fallback if Pillow is not installed or image creation fails
            print(f"Error loading placeholder image: {e}. Make sure 'Pillow' is installed (pip install Pillow).")
            self.waveform_label = tk.Label(waveform_frame, text="Image Load Error\n(Need Pillow)", bg="#34495e", fg="red")
            self.waveform_label.pack(expand=True, fill="both", padx=5, pady=5)

        # --- Panel 5 (NEW): Entropy Classification Overlay ---
        classification_frame = ttk.LabelFrame(main_frame, text="Entropy Classification", style="Dark.TFrame", padding="10")
        classification_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="nsew") # Spanning two rows

        self.prob_stall_label = ttk.Label(classification_frame, text="Prob. of STALL: Waiting...", style="Big.Dark.TLabel", anchor="center")
        self.prob_stall_label.pack(pady=(10, 5))

        # Use the "Vertical.TProgressbar" style.
        self.prob_stall_meter = ttk.Progressbar(classification_frame, orient="vertical", length=150, mode="determinate", style="Vertical.TProgressbar")
        self.prob_stall_meter.pack(padx=10, pady=5, fill="y", expand=True) # Vertical progress bar
        self.prob_stall_meter["maximum"] = 100 # Percentage

        self.classification_info_label = ttk.Label(classification_frame, text="Based on Entropy Score", style="Info.TLabel")
        self.classification_info_label.pack(pady=(5, 0))

        # --- Configure Grid Weights for Resizing ---
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=2) # Giving more weight to the first two columns
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_columnconfigure(2, weight=1) # Giving classification panel relatively less weight

        # --- Real-time Log Stream Handling ---
        self.log_queue = queue.Queue()
        self.log_reader_thread = None
        self.stop_event = threading.Event() # Event to signal thread to stop

        # Start reading the log file in a separate thread
        self.start_log_reader()
        # Periodically check the queue for new log entries and update GUI
        self.after(100, self.process_queue) # This schedules the first call after 100ms

    def clear_log_file(self):
        """Clears the log file to ensure fresh start."""
        try:
            with open(self.log_filename, 'w') as f:
                pass  # Just create/clear the file
            print(f"Cleared log file: {self.log_filename}")
        except Exception as e:
            print(f"Error clearing log file: {e}")

    def start_log_reader(self):
        """Starts a new thread to read the log file."""
        if self.log_reader_thread is None or not self.log_reader_thread.is_alive():
            print(f"Starting log reader thread for {self.log_filename}")
            # Ensure the file exists before attempting to read it
            if not os.path.exists(self.log_filename):
                print(f"Log file '{self.log_filename}' not found. Creating empty file.")
                try:
                    with open(self.log_filename, 'w') as f:
                        pass # Create the file
                except IOError as e:
                    print(f"Error creating log file: {e}")
                    # If we can't create it, there's no point proceeding with the reader
                    return

            self.log_reader_thread = threading.Thread(target=self._read_log_file_continuously,
                                                      args=(self.log_filename, self.log_queue, self.stop_event),
                                                      daemon=True) # Daemon thread exits with main program
            self.log_reader_thread.start()

    def _read_log_file_continuously(self, filename, q, stop_event):
        """Reads log file updates line by line and puts them into a queue,
        processing existing content first."""
        
        try:
            with open(filename, 'r') as f:
                print(f"Monitoring '{filename}' for new content...")
                
                # Continuously monitor for new appended lines
                while not stop_event.is_set():
                    line = f.readline()
                    if not line:
                        time.sleep(0.01) # Wait a bit if no new lines
                        continue
                    if line.strip(): # Only process non-empty lines
                        print(f"New log line detected: {line.strip()}")
                        q.put(line.strip()) # Put the new line into the queue
        except Exception as e:
            print(f"Error reading log file in thread: {e}")

    def process_queue(self):
        """Checks the queue for new log entries and updates the GUI."""
        try:
            # Process all available items in the queue
            while True:
                log_entry = self.log_queue.get_nowait() # Get without blocking
                self.parse_and_update_gui(log_entry)
        except queue.Empty:
            pass # No more items in the queue
        finally:
            # Schedule the next check (e.g., every 100ms)
            self.after(100, self.process_queue) # Reschedule yourself

    def parse_and_update_gui(self, log_entry):
        """Parses a log entry and updates the dashboard GUI elements."""
        try:
            # Expected format: [Cycle 123] State: STALL | Entropy: 190 | Trigger: analog
            parts = log_entry.split(' | ')
            
            # Now, after splitting by ' | ', we expect exactly 3 parts
            if len(parts) != 3:
                print(f"Skipping malformed log entry (incorrect number of parts): {log_entry}")
                return

            # Extract Cycle and State from the first part (e.g., "[Cycle 1] State: OK")
            first_part_components = parts[0].split('] State: ')
            if len(first_part_components) < 2:
                print(f"Skipping malformed log entry (bad first part components): {log_entry}")
                return
            cycle_str = first_part_components[0].replace('[Cycle ', '')
            state_str = first_part_components[1]

            # Extract Entropy from the second part (e.g., "Entropy: 73")
            entropy_str = parts[1].split(': ')[1]

            # Extract Trigger from the third part (e.g., "Trigger: Analog")
            trigger_str = parts[2].split(': ')[1]

            cycle = int(cycle_str)
            entropy_score = int(entropy_str)

            # --- ADDED PRINT STATEMENT FOR DEBUGGING ---
            print(f"Processing Cycle: {cycle}, State: {state_str}, Entropy: {entropy_score}, Trigger: {trigger_str}")
            # --- END ADDED PRINT STATEMENT ---

            # Update FSM State
            self.fsm_state_label.config(text=state_str)
            if state_str == "OK":
                self.fsm_state_label.config(style="Green.TLabel")
            elif state_str == "STALL":
                self.fsm_state_label.config(style="Orange.TLabel")
            elif state_str in ["FLUSH", "LOCK"]: # Handle both FLUSH and LOCK as red
                self.fsm_state_label.config(style="Red.TLabel")
            else: # Fallback for unknown states
                self.fsm_state_label.config(style="Big.Dark.TLabel") # Default dark style
            self.cycle_label.config(text=f"Cycle: {cycle}")

            # Update Entropy Score
            self.entropy_value_label.config(text=str(entropy_score))
            self.entropy_meter["value"] = entropy_score
            if entropy_score > 180:
                self.entropy_status_label.config(text="High Entropy")
                # Map to the default TProgressbar style for horizontal changes
                self.style.map("TProgressbar", background=[('!disabled', '#e74c3c')]) # Red for high entropy
            elif entropy_score > 120:
                self.entropy_status_label.config(text="Elevated")
                self.style.map("TProgressbar", background=[('!disabled', '#f39c12')]) # Orange for elevated
            else:
                self.entropy_status_label.config(text="Normal")
                self.style.map("TProgressbar", background=[('!disabled', '#2ecc71')]) # Green for normal

            # Update Override Source
            self.override_source_label.config(text=trigger_str)

            # NEW: Update Entropy Classification Overlay
            prob_stall = min(100, round((entropy_score / 255) * 100)) # Scale to 0-100%
            self.prob_stall_label.config(text=f"Prob. of STALL: {prob_stall}%")
            self.prob_stall_meter["value"] = prob_stall
            
            # Map to "Vertical.TProgressbar" style for vertical changes
            if prob_stall > 70:
                self.style.map("Vertical.TProgressbar", background=[('!disabled', '#e74c3c')]) # High risk, red
            elif prob_stall > 40:
                self.style.map("Vertical.TProgressbar", background=[('!disabled', '#f39c12')]) # Medium risk, orange
            else:
                self.style.map("Vertical.TProgressbar", background=[('!disabled', '#3498db')]) # Low risk, blue

        except Exception as e:
            print(f"Error parsing log entry '{log_entry}': {e}")

    def on_closing(self):
        """Handles proper shutdown when the window is closed."""
        print("Closing dashboard. Signalling log reader thread to stop.")
        self.stop_event.set() # Set the event to stop the thread
        if self.log_reader_thread and self.log_reader_thread.is_alive():
            self.log_reader_thread.join(timeout=1.0) # Give thread a chance to finish
        self.destroy()

if __name__ == "__main__":
    app = FSMDashboard()
    app.protocol("WM_DELETE_WINDOW", app.on_closing) # Handle window closing event
    app.mainloop()