"""
MedStudy Pro - Medical Typography System
Manages a professional and consistent font hierarchy for the application.
"""

import customtkinter as ctk

class MedicalTypography:
    """
    Manages a professional font system for MedStudy Pro.
    Provides a consistent hierarchy of fonts with appropriate fallbacks
    for cross-platform compatibility.
    """
    
    # Font family with fallbacks for professional appearance
    FONT_FAMILY = (
        "Segoe UI Variable",  # Modern Windows 11
        "Inter",             # Professional web font
        "SF Pro Display",    # macOS system font
        "Roboto",            # Google/Android standard
        "Segoe UI",         # Classic Windows
        "Arial"              # Universal fallback
    )
    
    # Code/Data specific font family
    CODE_FONT_FAMILY = (
        "Consolas",
        "Monaco",
        "Courier New"
    )

    def __init__(self):
        """Initializes the complete medical font system."""
        
        self.fonts = {
            # Display & Headings
            "display_32_bold": ctk.CTkFont(family=self.FONT_FAMILY, size=32, weight="bold"),
            "heading_24_bold": ctk.CTkFont(family=self.FONT_FAMILY, size=24, weight="bold"),
            "heading_20_bold": ctk.CTkFont(family=self.FONT_FAMILY, size=20, weight="bold"),
            "heading_18_bold": ctk.CTkFont(family=self.FONT_FAMILY, size=18, weight="bold"),
            "heading_16_bold": ctk.CTkFont(family=self.FONT_FAMILY, size=16, weight="bold"),
            
            # Body Text
            "body_16_normal": ctk.CTkFont(family=self.FONT_FAMILY, size=16, weight="normal"),
            "body_15_normal": ctk.CTkFont(family=self.FONT_FAMILY, size=15, weight="normal"),
            "body_14_normal": ctk.CTkFont(family=self.FONT_FAMILY, size=14, weight="normal"),
            "body_14_medium": ctk.CTkFont(family=self.FONT_FAMILY, size=14, weight="bold"), # CTkFont uses 'bold' for medium weight
            "body_13_normal": ctk.CTkFont(family=self.FONT_FAMILY, size=13, weight="normal"),
            "body_13_medium": ctk.CTkFont(family=self.FONT_FAMILY, size=13, weight="bold"),
            
            # Caption & Small Text
            "caption_12_normal": ctk.CTkFont(family=self.FONT_FAMILY, size=12, weight="normal"),
            "caption_11_normal": ctk.CTkFont(family=self.FONT_FAMILY, size=11, weight="normal"),
            "caption_10_normal": ctk.CTkFont(family=self.FONT_FAMILY, size=10, weight="normal"),
            
            # Buttons
            "button_14_bold": ctk.CTkFont(family=self.FONT_FAMILY, size=14, weight="bold"),
            "button_13_bold": ctk.CTkFont(family=self.FONT_FAMILY, size=13, weight="bold"),
            
            # Code/Data
            "code_13_normal": ctk.CTkFont(family=self.CODE_FONT_FAMILY, size=13, weight="normal"),
            "code_12_normal": ctk.CTkFont(family=self.CODE_FONT_FAMILY, size=12, weight="normal"),
        }

    def get_font(self, style: str) -> ctk.CTkFont:
        """
        Retrieves a pre-configured CTkFont object by its style name.

        Args:
            style: The name of the font style (e.g., "heading_24_bold").

        Returns:
            The corresponding CTkFont object, or a default body font if the style is not found.
        """
        return self.fonts.get(style, self.fonts["body_14_normal"])

    def apply_medical_styling(self, widget, style: str):
        """
        Applies a font style directly to a CustomTkinter widget.

        Args:
            widget: The CustomTkinter widget to apply the font to.
            style: The name of the font style.
        """
        font = self.get_font(style)
        if font:
            widget.configure(font=font)