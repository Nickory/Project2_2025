# SoilSensorEmail_GUI.py
# Use comment: run it in python environment
# Program Title: Agile Raspberry Pi Plant Moisture Sensor with Email Notification
# Program Description: This program uses a Raspberry Pi with a soil moisture sensor to monitor plant soil moisture levels. It sends email notifications at scheduled times (default: 07:00, 10:00, 13:00, 16:00) to report whether the plant needs watering. A Tkinter-based GUI displays the current status, last check time, next scheduled check, email status, and allows users to manage the notification schedule, perform manual checks, and run diagnostics. The program supports both real sensor input and a fallback mode if the sensor is unavailable.
# Name: Ziheng Wang
# NuistStudentID: 202283890020
# SETUID: 20109669
# Course & Year: Project Semester 3 2025
# Date: 20/4/25

import tkinter as tk
from tkinter import ttk  # Import themed Tkinter widgets
from tkinter import font as tkFont # For font management
from tkinter import messagebox # For potential pop-up messages
import time
import smtplib
import threading
from email.message import EmailMessage
from datetime import datetime, timedelta

# --- Configuration ---
# Try importing GPIO, handle gracefully if not on RPi or library not installed
try:
    import RPi.GPIO as GPIO
    ON_RASPBERRY_PI = True
    # GPIO Setup
    MOISTURE_SENSOR_PIN = 4 # Use the same GPIO pin as your original script
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN)
except (ImportError, RuntimeError):
    ON_RASPBERRY_PI = False
    print("WARNING: RPi.GPIO library not found or not running on Raspberry Pi. Sensor functionality disabled.")

# Email Configuration (Use your actual credentials)
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SENDER_EMAIL = "3119349688@qq.com" # Replace with your QQ email
SENDER_PASSWORD = "okhhgidjogtndfid" # Replace with your QQ email authorization code
RECIPIENT_EMAIL = "2563373919@qq.com" # Replace with recipient email

# Default Notification Schedule (24-hour format "HH:MM")
DEFAULT_CHECK_TIMES = ["07:00", "10:00", "13:00", "16:00"]

# --- Main Application Class ---
class SoilMoistureApp(tk.Tk): # Inherit from tk.Tk
    def __init__(self):
        super().__init__()

        # --- Internal State ---
        self.schedule_times = sorted(DEFAULT_CHECK_TIMES.copy())
        self.last_check_time_str = "Never"
        self.next_check_time_str = "Calculating..."
        self.current_status = "Initializing..."
        self.email_status = "Idle"
        self.monitoring_active = True # Flag to control the background thread
        self.sensor_available = ON_RASPBERRY_PI

        # --- Style Configuration (Optional, for ttk) ---
        self.style = ttk.Style(self)
        # You can try different themes if available on your system
        # print(self.style.theme_names()) # See available themes
        # self.style.theme_use('clam') # Example: 'clam', 'alt', 'default', 'classic'

        # --- Font Configuration ---
        self.title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
        self.label_font = tkFont.Font(family="Helvetica", size=12)
        self.status_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
        self.small_font = tkFont.Font(family="Helvetica", size=10)

        # --- Window Configuration ---
        self.title("Soil Moisture Monitor (Tkinter)")
        self.geometry("500x500") # Adjusted size for standard widgets
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close

        # --- GUI Widgets ---
        self.create_widgets()

        # --- Start Background Monitoring ---
        self.update_schedule_display() # Initial display
        self.update_next_check_time_label() # Initial calculation
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()

        # --- Initial Sensor Check ---
        if self.sensor_available:
            self.run_check(is_scheduled=False) # Perform an initial check on startup
        else:
            self.update_status_display("Sensor N/A")


    def create_widgets(self):
        """Create and arrange all GUI elements using tkinter/ttk."""

        # --- Main Frame (using ttk for better spacing/theming) ---
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill="both", expand=True)

        # --- Title ---
        title_label = ttk.Label(main_frame, text="🌿 Plant Monitor 🌿", font=self.title_font, anchor="center")
        title_label.pack(pady=(5, 15), fill="x")

        # --- Status Section ---
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(pady=5, padx=5, fill="x")

        status_title_label = ttk.Label(status_frame, text="Current Status:", font=self.label_font)
        status_title_label.pack(side="left", padx=(0, 5))

        self.status_label = ttk.Label(status_frame, text=self.current_status, font=self.status_font, foreground="gray")
        self.status_label.pack(side="left", padx=(0, 10))

        # --- Time Information Section ---
        time_frame = ttk.Frame(main_frame, padding="5 5 5 5")
        # Add a border for visual separation (optional)
        time_frame['borderwidth'] = 1
        time_frame['relief'] = 'groove'
        time_frame.pack(pady=10, padx=5, fill="x")

        last_check_label_desc = ttk.Label(time_frame, text="Last Check:", font=self.label_font)
        last_check_label_desc.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.last_check_label = ttk.Label(time_frame, text=self.last_check_time_str, font=self.label_font)
        self.last_check_label.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        next_check_label_desc = ttk.Label(time_frame, text="Next Scheduled Check:", font=self.label_font)
        next_check_label_desc.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.next_check_label = ttk.Label(time_frame, text=self.next_check_time_str, font=self.label_font)
        self.next_check_label.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        # Configure column 1 to expand and take available space if needed
        time_frame.columnconfigure(1, weight=1)


        # --- Manual Actions ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(pady=10, padx=5, fill="x")

        self.check_now_button = ttk.Button(action_frame, text="Check Moisture Now", command=lambda: self.run_check(is_scheduled=False))
        self.check_now_button.pack(side="left", padx=5, pady=5)
        if not self.sensor_available:
            self.check_now_button.configure(state="disabled")

        self.diagnostic_button = ttk.Button(action_frame, text="Run Diagnostics", command=self.run_diagnostic_test)
        self.diagnostic_button.pack(side="left", padx=5, pady=5)

        # --- Schedule Management Section ---
        schedule_frame = ttk.LabelFrame(main_frame, text="Alert Schedule (HH:MM)", padding="10 10 10 10") # Use LabelFrame
        schedule_frame.pack(pady=10, padx=5, fill="both", expand=True)

        # --- Add/Remove Time Controls Frame ---
        schedule_control_frame = ttk.Frame(schedule_frame)
        schedule_control_frame.pack(fill="x", pady=(0, 10)) # Place controls above the text area

        # Hour selection (using ttk.Combobox)
        hour_options = [f"{h:02d}" for h in range(24)]
        self.hour_var = tk.StringVar(self)
        self.hour_combobox = ttk.Combobox(schedule_control_frame, textvariable=self.hour_var, values=hour_options, width=5, state="readonly")
        self.hour_combobox.set(hour_options[7]) # Default to 07
        self.hour_combobox.pack(side="left", padx=(0, 5))

        # Minute selection (using ttk.Combobox)
        minute_options = [f"{m:02d}" for m in range(0, 60, 15)] # Steps of 15 minutes
        self.minute_var = tk.StringVar(self)
        self.minute_combobox = ttk.Combobox(schedule_control_frame, textvariable=self.minute_var, values=minute_options, width=5, state="readonly")
        self.minute_combobox.set(minute_options[0]) # Default to 00
        self.minute_combobox.pack(side="left", padx=5)

        self.add_time_button = ttk.Button(schedule_control_frame, text="Add", width=8, command=self.add_schedule_time)
        self.add_time_button.pack(side="left", padx=5)

        self.remove_time_button = ttk.Button(schedule_control_frame, text="Remove", width=8, command=self.remove_schedule_time)
        self.remove_time_button.pack(side="left", padx=5)

        # --- Schedule Display Text Area ---
        self.schedule_text = tk.Text(schedule_frame, height=8, width=20, wrap=tk.WORD, borderwidth=1, relief="sunken")
        # Add Scrollbar
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=self.schedule_text.yview)
        self.schedule_text['yscrollcommand'] = scrollbar.set
        # Pack text area and scrollbar together
        scrollbar.pack(side="right", fill="y")
        self.schedule_text.pack(pady=5, padx=(0, 5), fill="both", expand=True)
        self.schedule_text.configure(state="disabled") # Make read-only initially


        # --- Email Status ---
        email_status_frame = ttk.Frame(main_frame)
        email_status_frame.pack(pady=(10, 0), padx=5, fill="x", side="bottom") # Anchor to bottom
        self.email_status_label = ttk.Label(email_status_frame, text=f"Email Status: {self.email_status}", font=self.small_font)
        self.email_status_label.pack(side="left")

    # --- Core Logic Methods (Largely unchanged, check adaptations below) ---

    def check_moisture(self):
        """
        Read soil moisture sensor and return status string.
        Returns 'Sensor N/A' if sensor is not available.
        (Identical logic to previous version)
        """
        if not self.sensor_available:
            return "Sensor N/A"

        try:
            # Reading the sensor: HIGH means dry, LOW means wet (for many common sensors)
            if GPIO.input(MOISTURE_SENSOR_PIN):
                return "Soil is DRY - Water NEEDED"
            else:
                return "Soil is WET - No water needed"
        except Exception as e:
            print(f"ERROR: Could not read sensor: {e}")
            # Optionally show a message box:
            # messagebox.showerror("Sensor Error", f"Could not read sensor: {e}")
            return "Sensor Error"

    def send_alert_email(self, status, is_test=False):
        """
        Send email notification with proper English formatting.
        (Identical logic to previous version)
        """
        self.update_email_status("Sending...")
        try:
            email = EmailMessage()
            email['From'] = SENDER_EMAIL
            email['To'] = RECIPIENT_EMAIL

            if is_test:
                email['Subject'] = "🛠️ Plant Monitor - System Test"
                email_content = f"""
                SYSTEM DIAGNOSTIC TEST:
                - Test Triggered: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                - Message: {status}

                This is a test email to confirm functionality.
                """
            else:
                email['Subject'] = "🌿 Plant Watering Alert 🌿"
                email_content = f"""
                PLANT STATUS UPDATE:
                - Condition: {status}
                - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                ACTION REQUIRED:
                { 'Please water your plant!' if 'NEEDED' in status else 'Soil moisture is adequate. No action needed.' }
                """

            email.set_content(email_content.strip())

            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server: # Added timeout
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(email)
            print(f"✅ Alert email sent: {status}")
            self.update_email_status("Sent Successfully")

        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP Authentication Failed. Check email/password/authorization code."
            print(f"ERROR: {error_msg}")
            self.update_email_status("Authentication Error")
            # Optionally show error in GUI:
            # messagebox.showerror("Email Error", error_msg)
        except Exception as e:
            error_msg = f"Failed to send email: {e}"
            print(f"ERROR: {error_msg}")
            self.update_email_status(f"Failed: {type(e).__name__}")
            # Optionally show error in GUI:
            # messagebox.showerror("Email Error", error_msg)


    def run_check(self, is_scheduled=True):
        """
        Performs a moisture check, updates GUI, and sends email if needed.
        (Identical logic to previous version)
        """
        print(f"Running check (Scheduled: {is_scheduled})...")
        status = self.check_moisture()
        self.update_status_display(status)
        self.update_last_check_time() # Update last check time whenever a check runs

        # Send email only on scheduled checks OR if manually triggered AND water is needed
        if status != "Sensor N/A" and status != "Sensor Error":
            if is_scheduled or ('NEEDED' in status and not is_scheduled):
                 # Run email sending in a separate thread to avoid blocking GUI
                email_thread = threading.Thread(target=self.send_alert_email, args=(status,), daemon=True)
                email_thread.start()
            elif not is_scheduled:
                 self.update_email_status("Manual check - OK") # Update status if manual check is ok

    def run_diagnostic_test(self):
        """
        Run comprehensive system test in a separate thread.
        (Identical logic to previous version)
        """
        print("\n=== Running System Diagnostic ===")
        self.update_email_status("Running Diagnostics...")
        # Run diagnostics in a thread to avoid blocking
        diag_thread = threading.Thread(target=self._execute_diagnostics, daemon=True)
        diag_thread.start()

    def _execute_diagnostics(self):
        """
        Actual diagnostic steps (runs in background thread).
        (Identical logic to previous version)
        """
        # Test sensor reading
        test_status = self.check_moisture()
        print(f"Sensor Test Result: {test_status}")
        # Update GUI from main thread using 'after'
        self.after(0, self.update_status_display, f"Diag: {test_status}")

        # Test email functionality
        print("Testing email system...")
        self.send_alert_email(f"[DIAGNOSTIC TEST] Sensor reads: {test_status}", is_test=True)

        print("=== Diagnostic Complete ===\n")
        # Optionally update email status again after test completes
        # self.after(0, self.update_email_status, "Diagnostic Finished")

    def monitoring_loop(self):
        """
        Background loop to trigger scheduled checks.
        (Identical logic to previous version, uses self.after for GUI updates)
        """
        print("🌱 Monitoring loop started.")
        last_checked_minute_slot = None # Prevent multiple checks in the same minute

        while self.monitoring_active:
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")

            # Find the next scheduled check time (logic is the same)
            next_check_dt = self.calculate_next_check_datetime(now)

            if next_check_dt:
                 # Check if it's time for a scheduled check and hasn't been checked this minute
                if current_time_str in self.schedule_times and current_time_str != last_checked_minute_slot :
                    print(f"Scheduled check time reached: {current_time_str}")
                    self.run_check(is_scheduled=True)
                    last_checked_minute_slot = current_time_str # Mark this minute as checked
                    # Update last check time string immediately after triggering scheduled check
                    self.after(0, self._update_last_check_display, f"{current_time_str} (Scheduled)")

            # Reset checked minute slot when the minute changes
            if current_time_str != last_checked_minute_slot and now.second > 50:
                 last_checked_minute_slot = None # Allow checks in the next minute

            # Recalculate and update the 'Next Check' label periodically
            # Avoid doing this *every* loop iteration if possible, maybe every few seconds
            if now.second % 10 == 0: # Update every 10 seconds
                 self.update_next_check_time_label()

            # Sleep efficiently until the next potential check time or for a fixed interval
            time.sleep(1) # Check every second for responsiveness

        print("Monitoring loop stopped.")

    def calculate_next_check_datetime(self, current_datetime):
        """
        Calculates the datetime of the next scheduled check.
        (Identical logic to previous version)
        """
        if not self.schedule_times:
            return None

        now_time = current_datetime.time()
        today_str = current_datetime.strftime('%Y-%m-%d')
        next_check_dt = None

        # Check for the next time today
        for time_str in self.schedule_times:
            hour, minute = map(int, time_str.split(':'))
            scheduled_time = datetime.strptime(f"{today_str} {time_str}", '%Y-%m-%d %H:%M').time()
            if scheduled_time > now_time:
                next_check_dt = datetime.combine(current_datetime.date(), scheduled_time)
                break

        # If no more checks today, find the first one tomorrow
        if next_check_dt is None:
            first_time_str = self.schedule_times[0]
            tomorrow_date = current_datetime.date() + timedelta(days=1)
            next_check_dt = datetime.strptime(f"{tomorrow_date.strftime('%Y-%m-%d')} {first_time_str}", '%Y-%m-%d %H:%M')

        return next_check_dt


    # --- GUI Update Methods (Use standard tkinter/ttk configure methods) ---
    def update_status_display(self, status):
        """Updates the status label text and color."""
        self.current_status = status
        color = "gray" # Default/Info color name
        if "DRY" in status or "NEEDED" in status:
            color = "orange"
        elif "WET" in status or "adequate" in status:
            color = "green"
        elif "Error" in status or "N/A" in status:
            color = "red"

        # Ensure GUI updates happen on the main thread
        self.after(0, self._update_status_label_config, status, color)

    def _update_status_label_config(self, status, color):
        """Helper to update label config in main thread."""
        self.status_label.config(text=status, foreground=color) # Use 'config' and 'foreground'

    def update_last_check_time(self):
        """Updates the last check time label."""
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         # Call helper via 'after' to ensure main thread execution
        self.after(0, self._update_last_check_display, now_str)


    def _update_last_check_display(self, time_str):
        """Helper to update last check label in main thread."""
        self.last_check_time_str = time_str # Update internal state as well
        self.last_check_label.config(text=time_str) # Use 'config'


    def update_next_check_time_label(self):
        """Calculates and updates the next check time label."""
        now = datetime.now()
        next_dt = self.calculate_next_check_datetime(now)
        if next_dt:
            self.next_check_time_str = next_dt.strftime('%Y-%m-%d %H:%M')
        else:
            self.next_check_time_str = "No schedule set"

        # Ensure GUI updates happen on the main thread
        self.after(0, self._update_next_check_label_config, self.next_check_time_str)

    def _update_next_check_label_config(self, time_str):
        """Helper to update next check label in main thread."""
        self.next_check_label.config(text=time_str) # Use 'config'


    def update_email_status(self, status):
        """Updates the email status label."""
        self.email_status = status
        # Ensure GUI updates happen on the main thread
        self.after(0, self._update_email_label_config, f"Email Status: {status}")

    def _update_email_label_config(self, status_text):
         """Helper to update email status label in main thread."""
         self.email_status_label.config(text=status_text) # Use 'config'


    def update_schedule_display(self):
         """Updates the schedule text area display."""
         # Ensure GUI updates happen on the main thread
         self.after(0, self._update_schedule_text_content)

    def _update_schedule_text_content(self):
        """Helper to update schedule text area in main thread."""
        self.schedule_text.config(state=tk.NORMAL) # Enable writing (use tk constants)
        self.schedule_text.delete("1.0", tk.END) # Clear existing content (use tk constants)
        if self.schedule_times:
             display_text = "\n".join(self.schedule_times)
             self.schedule_text.insert("1.0", display_text) # Insert at the beginning
        else:
             self.schedule_text.insert("1.0", "(No times scheduled)")
        self.schedule_text.config(state=tk.DISABLED) # Disable writing (use tk constants)


    # --- Schedule Management Methods ---
    def add_schedule_time(self):
        """Adds a time selected via comboboxes to the schedule."""
        # Get values directly from the ttk.Combobox variables
        hour = self.hour_var.get()
        minute = self.minute_var.get()

        # Basic validation
        if not hour or not minute:
            messagebox.showwarning("Input Error", "Please select both an hour and a minute.")
            return

        new_time = f"{hour}:{minute}"

        if new_time not in self.schedule_times:
            self.schedule_times.append(new_time)
            self.schedule_times.sort() # Keep the list sorted
            print(f"Added schedule time: {new_time}")
            self.update_schedule_display()
            self.update_next_check_time_label() # Recalculate next check
        else:
            print(f"Time {new_time} already in schedule.")
            messagebox.showinfo("Info", f"Time {new_time} is already in the schedule.")


    def remove_schedule_time(self):
        """Removes the time selected via comboboxes from the schedule."""
        hour = self.hour_var.get()
        minute = self.minute_var.get()

        # Basic validation
        if not hour or not minute:
            messagebox.showwarning("Input Error", "Please select both an hour and a minute to remove.")
            return

        time_to_remove = f"{hour}:{minute}"

        if time_to_remove in self.schedule_times:
            self.schedule_times.remove(time_to_remove)
            print(f"Removed schedule time: {time_to_remove}")
            self.update_schedule_display()
            self.update_next_check_time_label() # Recalculate next check
        else:
            print(f"Time {time_to_remove} not found in schedule.")
            messagebox.showinfo("Info", f"Time {time_to_remove} was not found in the schedule.")


    # --- Window Closing Handler ---
    def on_closing(self):
        """Handles cleanup when the window is closed."""
        print("Closing application...")
        self.monitoring_active = False # Signal the monitoring thread to stop

        if ON_RASPBERRY_PI:
            try:
                GPIO.cleanup()
                print("GPIO resources cleaned up.")
            except Exception as e:
                print(f"Error during GPIO cleanup: {e}")
        self.destroy() # Close the Tkinter window


# --- Main Execution ---
if __name__ == "__main__":
    app = SoilMoistureApp()
    app.mainloop()
