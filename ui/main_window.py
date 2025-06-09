import customtkinter as ctk

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
        self.tab_view.configure(segmented_button_selected_color=PRIMARY_COLOR)
        self.tab_view.configure(segmented_button_unselected_color=BACKGROUND_COLOR)
        self.tab_view.configure(segmented_button_selected_hover_color=ACCENT_COLOR)
        self.tab_view.configure(segmented_button_unselected_hover_color=ACCENT_COLOR)

        self.tab_view.add("Dashboard")
        self.tab_view.add("Planner")
        self.tab_view.add("Sessions")
        self.tab_view.add("Exams")
        self.tab_view.add("Progress")

        # Placeholder labels for each tab
        dashboard_label = ctk.CTkLabel(self.tab_view.tab("Dashboard"), text="Welcome to the Dashboard", font=ctk.CTkFont(size=18))
        dashboard_label.pack(expand=True, fill="both", padx=20, pady=20)

        planner_label = ctk.CTkLabel(self.tab_view.tab("Planner"), text="Welcome to the Planner", font=ctk.CTkFont(size=18))
        planner_label.pack(expand=True, fill="both", padx=20, pady=20)

        sessions_label = ctk.CTkLabel(self.tab_view.tab("Sessions"), text="Welcome to Sessions", font=ctk.CTkFont(size=18))
        sessions_label.pack(expand=True, fill="both", padx=20, pady=20)

        exams_label = ctk.CTkLabel(self.tab_view.tab("Exams"), text="Welcome to Exams", font=ctk.CTkFont(size=18))
        exams_label.pack(expand=True, fill="both", padx=20, pady=20)

        progress_label = ctk.CTkLabel(self.tab_view.tab("Progress"), text="Welcome to Progress", font=ctk.CTkFont(size=18))
        progress_label.pack(expand=True, fill="both", padx=20, pady=20)

        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

if __name__ == "__main__":
    app = MainWindow(config=None)
    app.mainloop()
