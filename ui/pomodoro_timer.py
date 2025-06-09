import customtkinter as ctk
import tkinter as tk # For canvas later, but not used in this part

# Attempt to import FontManager, handle if not found during standalone testing
try:
    from ui.font_manager import FontManager
except ImportError:
    FontManager = None # Placeholder if running standalone or FontManager is not found

# Define colors (or import from a central config if available)
PRIMARY_COLOR = "#1E3A8A"
SUCCESS_COLOR = "#10B981"
ACCENT_COLOR = "#06B6D4"
BACKGROUND_COLOR = "#FEFCF9" # Main background for app
TEXT_COLOR = "#1F2937"
POMODORO_BG = "#F0F4F8" # A slightly different background for the timer component itself

class PomodoroTimer(ctk.CTkFrame):
    def __init__(self, master, config=None, font_manager=None):
        super().__init__(master, fg_color=POMODORO_BG)
        self.config = config
        
        if font_manager:
            self.font_manager = font_manager
        elif FontManager: # If imported successfully
            self.font_manager = FontManager()
        else: # Fallback if FontManager is completely unavailable
            self.font_manager = None # Or create default CTkFonts

        # Timer State Variables
        self.study_duration_options = {"25 min": 25 * 60, "45 min": 45 * 60, "60 min": 60 * 60}
        self.selected_study_duration = list(self.study_duration_options.values())[0] # Default to 25 min
        
        self.short_break_duration = 5 * 60
        self.long_break_duration = 15 * 60
        self.cycles_for_long_break = 4
        self.current_cycle = 0 # Number of study sessions completed in the current set for long break
        
        self.study_session_types = ["General Study", "Reading", "Memorization", "Practice Questions"]
        self.selected_session_type = tk.StringVar(value=self.study_session_types[0])

        self.time_left = self.selected_study_duration
        self.current_mode_total_duration = self.selected_study_duration # Stores the total duration for the current mode
        self.is_running = False
        self.current_mode = "Study" # Study, Short Break, Long Break
        self._timer_job = None

        # Active Recall State
        self.active_recall_interval = 10 * 60  # 10 minutes in seconds
        self.active_recall_counter = 0
        self.active_recall_popup_window = None # To keep track of the popup

        # Canvas attributes
        self.canvas_size = 200 # Diameter of the progress ring
        self.ring_thickness = 15

        # UI Elements
        self._setup_ui()

    def _get_font(self, style_name):
        if self.font_manager:
            font = self.font_manager.get_font(style_name)
            if font:
                return font
        
        # Fallback fonts if FontManager is not available or style_name is not found
        # Ensure this part is robust
        fallbacks = {
            "header_24_bold": ctk.CTkFont(family="Arial", size=24, weight="bold"),
            "header_48_bold": ctk.CTkFont(family="Arial", size=48, weight="bold"),
            "body_14_regular": ctk.CTkFont(family="Arial", size=14),
            "body_12_regular": ctk.CTkFont(family="Arial", size=12),
            "body_14_medium": ctk.CTkFont(family="Arial", size=14, weight="bold"),
        }
        return fallbacks.get(style_name, ctk.CTkFont(family="Arial", size=12))


    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1) # Make content centered
        # Row configuration will be implicitly handled by order or can be fine-tuned if needed.
        # Example: self.grid_rowconfigure(X, weight=Y) for specific rows

        # Duration Selection (Row 0)
        duration_keys = list(self.study_duration_options.keys())
        self.duration_selector = ctk.CTkSegmentedButton(
            self,
            values=duration_keys,
            command=self._select_duration,
            font=self._get_font("body_12_regular"),
            selected_color=PRIMARY_COLOR,
            selected_hover_color=ACCENT_COLOR,
            unselected_hover_color=ACCENT_COLOR
        )
        self.duration_selector.set(duration_keys[0])
        self.duration_selector.grid(row=0, column=0, pady=(20,10), padx=20, sticky="ew")

        # Canvas for circular progress
        self.progress_canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=POMODORO_BG, # Use Pomodoro_BG for canvas background
            highlightthickness=0 # No border for the canvas widget itself
        )
        self.progress_canvas.grid(row=1, column=0, pady=20, sticky="nsew")
        
        # Time Display (Large Label) - Placed over the canvas
        self.time_display_label = ctk.CTkLabel(
            self, # Parent is still self (the PomodoroTimer frame)
            text=self._format_time(self.time_left),
            font=self._get_font("header_48_bold"),
            fg_color="transparent" # Make its background transparent
        )
        self.time_display_label.grid(row=1, column=0, sticky="nsew") # Same cell as canvas
        self.time_display_label.lift() # Ensure label is on top of the canvas

        # Initial drawing of the progress ring
        self._draw_progress_ring(self.time_left, self.current_mode_total_duration)

        # Control Buttons Frame (Row 2)
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=2, column=0, pady=10)

        self.start_button = ctk.CTkButton(
            controls_frame,
            text="Start",
            command=self.start_timer,
            font=self._get_font("body_14_medium"),
            fg_color=SUCCESS_COLOR,
            hover_color=ACCENT_COLOR
        )
        self.start_button.pack(side="left", padx=5)

        self.pause_button = ctk.CTkButton(
            controls_frame,
            text="Pause",
            command=self.pause_timer,
            font=self._get_font("body_14_medium"),
            state="disabled"
        )
        self.pause_button.pack(side="left", padx=5)

        self.reset_button = ctk.CTkButton(
            controls_frame,
            text="Reset",
            command=self.reset_timer,
            font=self._get_font("body_14_medium"),
            state="disabled" # Initially disabled, enabled when timer starts or is paused
        )
        self.reset_button.pack(side="left", padx=5)
        
        # Completed Cycles Display (Row 3)
        self.cycles_display_label = ctk.CTkLabel(
            self,
            text=f"Completed Cycles: {self.current_cycle}",
            font=self._get_font("body_12_regular")
        )
        self.cycles_display_label.grid(row=3, column=0, pady=5)
        
        # Status Label (Row 4)
        self.status_label = ctk.CTkLabel(
            self,
            text="Select study duration and press Start.",
            font=self._get_font("body_14_regular")
        )
        self.status_label.grid(row=4, column=0, pady=(10,5)) # Adjusted pady

        # Session Type Label (Row 5)
        session_type_label = ctk.CTkLabel(self, text="Session Type:", font=self._get_font("body_12_regular"))
        session_type_label.grid(row=5, column=0, pady=(5,0), padx=20, sticky="sw")

        # Session Type OptionMenu (Row 6)
        self.session_type_menu = ctk.CTkOptionMenu(
            self,
            values=self.study_session_types,
            variable=self.selected_session_type,
            command=self._select_session_type,
            font=self._get_font("body_12_regular")
        )
        self.session_type_menu.grid(row=6, column=0, pady=(0,20), padx=20, sticky="ew")


    def _select_session_type(self, choice):
        # self.selected_session_type variable is automatically updated by CTkOptionMenu.
        print(f"Session type selected: {self.selected_session_type.get()}")

    def _select_duration(self, selected_key):
        if not self.is_running:
            self.selected_study_duration = self.study_duration_options[selected_key] # This is specific to "Study" mode
            self.time_left = self.selected_study_duration
            self.current_mode_total_duration = self.selected_study_duration
            self.current_mode = "Study" # Selecting duration always implies resetting to study mode
            
            self.time_display_label.configure(text=self._format_time(self.time_left))
            self._draw_progress_ring(self.time_left, self.current_mode_total_duration)
            self.status_label.configure(text=f"Study for {selected_key}. Press Start.")
            self.start_button.configure(text="Start Study") # Update button text
            self.reset_button.configure(state="disabled") # Ensure reset is disabled if duration changes before start

    def _format_time(self, total_seconds):
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _update_timer(self):
        if self.is_running and self.time_left > 0:
            self.time_left -= 1
            self.time_display_label.configure(text=self._format_time(self.time_left))
            self._draw_progress_ring(self.time_left, self.current_mode_total_duration)

            if self.current_mode == "Study":
                self.active_recall_counter += 1
                if self.active_recall_counter >= self.active_recall_interval:
                    self.pause_timer(is_active_recall=True) 
                    self._show_active_recall_popup()
                    self.active_recall_counter = 0 
            
            if self.is_running: # Check if still running (pause_timer might have changed it)
                self._timer_job = self.after(1000, self._update_timer)

        elif self.is_running and self.time_left == 0: # Timer reached zero
            self.is_running = False
            self._draw_progress_ring(self.time_left, self.current_mode_total_duration) # Final draw at zero
            
            if self.current_mode == "Study":
                self.current_cycle += 1
                self.cycles_display_label.configure(text=f"Completed Cycles: {self.current_cycle}")
                # print(f"Cycles completed: {self.current_cycle}") # For debugging
                if self.current_cycle % self.cycles_for_long_break == 0:
                    self._switch_mode("Long Break", self.long_break_duration)
                else:
                    self._switch_mode("Short Break", self.short_break_duration)
            else: # If it was a Short Break or Long Break
                self._switch_mode("Study", self.selected_study_duration)
            
            # UI is updated in _switch_mode to prompt user to start next session

    def _switch_mode(self, new_mode, duration):
        self.current_mode = new_mode
        self.time_left = duration
        self.current_mode_total_duration = duration

        self.time_display_label.configure(text=self._format_time(self.time_left))
        self._draw_progress_ring(self.time_left, self.current_mode_total_duration)
        
        mode_text = new_mode.replace("_", " ") # Make it user-friendly
        self.status_label.configure(text=f"{mode_text} session. Press 'Start {mode_text}' to begin.")
        self.start_button.configure(state="normal", text=f"Start {mode_text}")
        self.pause_button.configure(state="disabled", text="Pause") # Ensure pause is disabled
        self.reset_button.configure(state="normal") # Allow reset from a break

        if new_mode == "Study":
            self.duration_selector.configure(state="normal")
        else: # Short Break or Long Break
            self.duration_selector.configure(state="disabled")


    def start_timer(self):
        if not self.is_running:
            # If time_left is full for the current mode, it's a fresh start for this mode
            if self.time_left == self.current_mode_total_duration:
                 self.status_label.configure(text=f"{self.current_mode} session started ({self._format_time(self.time_left)})")
            else: # Resuming a paused session of the current mode
                 self.status_label.configure(text=f"Resumed {self.current_mode} ({self._format_time(self.time_left)})")
            
            self._draw_progress_ring(self.time_left, self.current_mode_total_duration)
            self.is_running = True
            self.active_recall_counter = 0 # Reset AR counter whenever timer starts/resumes
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal", text="Pause")
            self.reset_button.configure(state="normal")
            
            # Disable duration selector only if starting a Study session. Breaks should not allow duration change.
            if self.current_mode == "Study":
                self.duration_selector.configure(state="disabled") 
            
            self._update_timer()

    def pause_timer(self, is_active_recall=False):
        if self.is_running:
            self.is_running = False
            if self._timer_job:
                self.after_cancel(self._timer_job)
                self._timer_job = None
            
            if is_active_recall:
                self.status_label.configure(text="Active Recall! Pause for review.")
            else:
                self.status_label.configure(text=f"{self.current_mode} Paused ({self._format_time(self.time_left)})")
            
            self.start_button.configure(state="normal", text="Resume") 
            self.pause_button.configure(state="disabled")
            self.reset_button.configure(state="normal") 

    def reset_timer(self):
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None
        self.is_running = False
        
        if self.active_recall_popup_window is not None and self.active_recall_popup_window.winfo_exists():
            self.active_recall_popup_window.grab_release()
            self.active_recall_popup_window.destroy()
            self.active_recall_popup_window = None

        # Find the key corresponding to the current self.selected_study_duration
        current_duration_key = list(self.study_duration_options.keys())[list(self.study_duration_options.values()).index(self.selected_study_duration)]
        
        self.time_left = self.selected_study_duration 
        self.current_mode = "Study" 
        self.current_mode_total_duration = self.selected_study_duration
        self.current_cycle = 0 
        self.active_recall_counter = 0
        
        self.time_display_label.configure(text=self._format_time(self.time_left))
        self._draw_progress_ring(self.time_left, self.current_mode_total_duration)
        self.status_label.configure(text="Timer reset to Study. Select duration and press Start.")
        self.start_button.configure(state="normal", text="Start Study")
        self.pause_button.configure(state="disabled", text="Pause")
        self.reset_button.configure(state="disabled") 
        self.duration_selector.configure(state="normal")
        self.duration_selector.set(current_duration_key)

    def _show_active_recall_popup(self):
        if self.active_recall_popup_window is not None and self.active_recall_popup_window.winfo_exists():
            self.active_recall_popup_window.focus() 
            return

        self.active_recall_popup_window = ctk.CTkToplevel(self)
        self.active_recall_popup_window.title("Active Recall")
        
        popup_width = 350
        # popup_height = 200 # Auto-adjusts height
        # self.active_recall_popup_window.geometry(f"{popup_width}x{popup_height}") 
        
        self.active_recall_popup_window.attributes("-topmost", True) 
        self.active_recall_popup_window.protocol("WM_DELETE_WINDOW", self._handle_recall_popup_close)

        popup_frame = ctk.CTkFrame(self.active_recall_popup_window)
        popup_frame.pack(expand=True, fill="both", padx=20, pady=20)

        message_label = ctk.CTkLabel(
            popup_frame,
            text="Time for Active Recall!\n\nBriefly review what you've just studied.",
            font=self._get_font("body_14_regular"),
            wraplength=popup_width-60 
        )
        message_label.pack(pady=(10, 20))

        resume_button = ctk.CTkButton(
            popup_frame,
            text="Resume Study",
            command=self._handle_recall_popup_close,
            font=self._get_font("body_14_medium"),
            fg_color=SUCCESS_COLOR
        )
        resume_button.pack(pady=20)
        
        self.active_recall_popup_window.grab_set() 
        self.active_recall_popup_window.focus_force()
        self.active_recall_popup_window.lift()

    def _handle_recall_popup_close(self):
        if self.active_recall_popup_window is not None:
            self.active_recall_popup_window.grab_release()
            self.active_recall_popup_window.destroy()
            self.active_recall_popup_window = None
        
        # Ensure timer is not running from other sources and then start
        if not self.is_running: # Only start if it was genuinely paused for AR
            self.status_label.configure(text=f"Resuming {self.current_mode}...") 
            self.start_timer() 

    def _draw_progress_ring(self, current_value, max_value):
        # It's possible this method is called before canvas is fully initialized by Tkinter geometry manager
        # Add a check to ensure canvas is ready or defer drawing
        if not self.progress_canvas.winfo_exists() or self.progress_canvas.winfo_width() <= 1:
            self.after(50, lambda: self._draw_progress_ring(current_value, max_value)) # Try again shortly
            return

        self.progress_canvas.delete("all") # Clear previous drawings

        if max_value == 0: return # Avoid division by zero

        # Coordinates for the bounding box of the circle
        # Ensure canvas is square, use min(width, height) if it could be non-square
        # For simplicity, assuming self.canvas_size is actual drawing dimension
        canvas_draw_size = min(self.progress_canvas.winfo_width(), self.progress_canvas.winfo_height())
        if canvas_draw_size < self.ring_thickness * 2 : # if canvas not yet sized, use default
            canvas_draw_size = self.canvas_size

        x0 = self.ring_thickness / 2
        y0 = self.ring_thickness / 2
        x1 = canvas_draw_size - (self.ring_thickness / 2)
        y1 = canvas_draw_size - (self.ring_thickness / 2)
        
        # Ensure x0,y0,x1,y1 are positive, otherwise arc will not draw
        if x1 <= x0 or y1 <= y0:
             # print(f"Canvas size too small for ring thickness. {canvas_draw_size} vs {self.ring_thickness}")
             return


        # Background ring (full circle) - using a slightly lighter/muted color
        # A common approach is to use a lighter shade of the text color or a neutral gray.
        # For now, let's use a light gray, or a desaturated version of ACCENT_COLOR
        background_ring_color = "#E0E0E0" # Light gray

        self.progress_canvas.create_arc(
            x0, y0, x1, y1,
            start=90, extent=360, # Start at top, full circle
            style=tk.ARC,
            outline=background_ring_color, 
            width=self.ring_thickness
        )

        # Foreground progress arc
        progress_percentage = (current_value / max_value)
        extent_angle = 360 * progress_percentage

        if extent_angle > 0: # Only draw if there's progress
            # Ensure extent is not too small to be invisible or too large (max 359.9 for open arc)
            # For a full circle appearance when time is full, extent_angle should be close to 360.
            # Tkinter's arc seems to handle 360 fine for full circle.
            self.progress_canvas.create_arc(
                x0, y0, x1, y1,
                start=90, # Start from the top (12 o'clock)
                extent=-extent_angle, # Negative for clockwise from 12 o'clock.
                style=tk.ARC,
                outline=SUCCESS_COLOR, 
                width=self.ring_thickness
            )

if __name__ == '__main__':
    # Example usage for standalone testing
    app = ctk.CTk()
    app.title("Pomodoro Timer Test")
    app.geometry("400x500") # Adjusted for better visibility
    
    # Mock FontManager if not available (e.g. if ui.font_manager is not in PYTHONPATH)
    mock_fm_instance = None
    if FontManager is None: 
        print("FontManager not found, using MockFontManager for PomodoroTimer test.")
        class MockFontManager:
            def get_font(self, style_name):
                # Provide some basic CTkFont objects for testing
                fallbacks = {
                    "header_24_bold": ctk.CTkFont(family="Arial", size=24, weight="bold"),
                    "header_48_bold": ctk.CTkFont(family="Arial", size=48, weight="bold"),
                    "body_14_regular": ctk.CTkFont(family="Arial", size=14),
                    "body_12_regular": ctk.CTkFont(family="Arial", size=12),
                    "body_14_medium": ctk.CTkFont(family="Arial", size=14, weight="bold"),
                }
                return fallbacks.get(style_name, ctk.CTkFont(family="Arial", size=12))
        mock_fm_instance = MockFontManager()
    else:
        print("FontManager found, using it for PomodoroTimer test.")
        # If FontManager is available, we might still need a root window for it to init fonts.
        # The app instance above serves as the root.
        mock_fm_instance = FontManager()


    timer_frame = PomodoroTimer(app, font_manager=mock_fm_instance)
    timer_frame.pack(expand=True, fill="both", padx=10, pady=10)
    
    # Add a label to indicate if real or mock FontManager is used
    fm_status_text = "Using REAL FontManager" if FontManager is not None and mock_fm_instance is not None and isinstance(mock_fm_instance, FontManager) else "Using MOCK FontManager"
    fm_status_label = ctk.CTkLabel(app, text=fm_status_text, font=ctk.CTkFont(size=10))
    fm_status_label.pack(pady=(0,5))

    app.mainloop()
