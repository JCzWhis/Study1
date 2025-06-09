import customtkinter as ctk
from ui.font_manager import FontManager

# Note: CustomTkinter CTkLabel does not natively support text shadows.
# Line height is generally influenced by font choice and layout padding.

# Color Palette
PRIMARY_COLOR = "#1E3A8A"
SUCCESS_COLOR = "#10B981"
ACCENT_COLOR = "#06B6D4"
BACKGROUND_COLOR = "#FEFCF9"
TEXT_COLOR = "#1F2937"

class MainWindow(ctk.CTk):
    """Main application window for MedStudy Pro."""

    def __init__(self, config=None):
        super().__init__()
        self.config = config
        self.font_manager = FontManager()

        self.title("MedStudy Pro")
        self.geometry("1400x900")
        self.resizable(True, True)

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        try:
            self.iconbitmap("icon.ico")
        except Exception as e:
            print(f"Error setting icon: {e}")
            # You could also use self.logger here if you pass the logger to MainWindow

        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        
        tab_font = self.font_manager.get_font("body_14_medium")
        if tab_font:
            self.tab_view.configure(font=tab_font)
            
        self.tab_view.configure(segmented_button_selected_color=PRIMARY_COLOR)
        self.tab_view.configure(segmented_button_unselected_color=BACKGROUND_COLOR)
        self.tab_view.configure(segmented_button_selected_hover_color=ACCENT_COLOR)
        self.tab_view.configure(segmented_button_unselected_hover_color=ACCENT_COLOR)

        self.tab_view.add("Dashboard")
        self.tab_view.add("Planner")
        self.tab_view.add("Sessions")
        self.tab_view.add("Exams")
        self.tab_view.add("Progress")

        # Content for each tab
        # Dashboard Tab
        dashboard_tab = self.tab_view.tab("Dashboard")
        dashboard_title = ctk.CTkLabel(dashboard_tab, text="Dashboard", font=self.font_manager.get_font("header_20_bold"))
        dashboard_title.pack(pady=(20, 10), padx=20, anchor="w")
        dashboard_content = ctk.CTkLabel(dashboard_tab, text="Welcome to your MedStudy Pro Dashboard.\nTrack your overall progress and upcoming events here.", font=self.font_manager.get_font("body_14_regular"), justify="left")
        dashboard_content.pack(pady=5, padx=20, anchor="w", fill="x")

        # Planner Tab
        planner_tab = self.tab_view.tab("Planner")
        planner_title = ctk.CTkLabel(planner_tab, text="Study Planner", font=self.font_manager.get_font("header_20_bold"))
        planner_title.pack(pady=(20, 10), padx=20, anchor="w")
        planner_content = ctk.CTkLabel(planner_tab, text="Organize your study schedule, set goals, and track your learning activities.", font=self.font_manager.get_font("body_14_regular"), justify="left")
        planner_content.pack(pady=5, padx=20, anchor="w", fill="x")

        # Sessions Tab
        sessions_tab = self.tab_view.tab("Sessions")
        sessions_title = ctk.CTkLabel(sessions_tab, text="Study Sessions", font=self.font_manager.get_font("header_20_bold"))
        sessions_title.pack(pady=(20, 10), padx=20, anchor="w")
        sessions_content = ctk.CTkLabel(sessions_tab, text="Manage focused study sessions. Use techniques like Pomodoro and active recall.", font=self.font_manager.get_font("body_14_regular"), justify="left")
        sessions_content.pack(pady=5, padx=20, anchor="w", fill="x")

        # Exams Tab
        exams_tab = self.tab_view.tab("Exams")
        exams_title = ctk.CTkLabel(exams_tab, text="Exam Preparation", font=self.font_manager.get_font("header_20_bold"))
        exams_title.pack(pady=(20, 10), padx=20, anchor="w")
        exams_content = ctk.CTkLabel(exams_tab, text="Prepare for your exams with mock tests, question banks, and performance analysis.", font=self.font_manager.get_font("body_14_regular"), justify="left")
        exams_content.pack(pady=5, padx=20, anchor="w", fill="x")

        # Progress Tab
        progress_tab = self.tab_view.tab("Progress")
        progress_title = ctk.CTkLabel(progress_tab, text="Progress Tracking", font=self.font_manager.get_font("header_20_bold"))
        progress_title.pack(pady=(20, 10), padx=20, anchor="w")
        progress_content = ctk.CTkLabel(progress_tab, text="Monitor your learning progress, identify strengths and weaknesses, and view detailed reports.", font=self.font_manager.get_font("body_14_regular"), justify="left")
        progress_content.pack(pady=5, padx=20, anchor="w", fill="x")

        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

if __name__ == "__main__":
    app = MainWindow(config=None)
    app.mainloop()