import customtkinter as ctk

class FontManager:
    """
    Manages fonts for the MedStudy Pro application, providing a consistent typography system.
    Uses "Segoe UI Variable" as the primary font, with "Inter" and "Segoe UI" as fallbacks.
    """

    PRIMARY_FONT = "Segoe UI Variable"
    FALLBACK_FONT_1 = "Inter"
    FALLBACK_FONT_2 = "Segoe UI"
    FALLBACK_FONT_GENERIC = "Arial" # A widely available sans-serif font

    def __init__(self):
        """Initializes all predefined font styles."""
        
        # Construct the font family string for CTkFont
        # CTkFont (via Tkinter) will try these fonts in order.
        _font_family_string = (
            f"{self.PRIMARY_FONT}, "
            f"{self.FALLBACK_FONT_1}, "
            f"{self.FALLBACK_FONT_2}, "
            f"{self.FALLBACK_FONT_GENERIC}"
        )

        self.fonts = {
            "header_24_bold": ctk.CTkFont(family=_font_family_string, size=24, weight="bold"),
            "header_20_bold": ctk.CTkFont(family=_font_family_string, size=20, weight="bold"),
            "header_18_bold": ctk.CTkFont(family=_font_family_string, size=18, weight="bold"),
            "header_16_bold": ctk.CTkFont(family=_font_family_string, size=16, weight="bold"),
            "body_14_regular": ctk.CTkFont(family=_font_family_string, size=14, weight="normal"),
            "body_14_medium": ctk.CTkFont(family=_font_family_string, size=14, weight="bold"), # CTkFont uses 'bold' for 'medium' if specific medium weight is not well supported
            "body_12_regular": ctk.CTkFont(family=_font_family_string, size=12, weight="normal"),
            "body_12_medium": ctk.CTkFont(family=_font_family_string, size=12, weight="bold"), # CTkFont uses 'bold' for 'medium'
            "small_11_regular": ctk.CTkFont(family=_font_family_string, size=11, weight="normal"),
            "small_10_regular": ctk.CTkFont(family=_font_family_string, size=10, weight="normal"),
        }

    def get_font(self, style_name: str) -> ctk.CTkFont:
        """
        Retrieves a pre-configured CTkFont object.

        Args:
            style_name: The name of the font style (e.g., "header_24_bold").

        Returns:
            The CTkFont object if found, otherwise None.
        """
        return self.fonts.get(style_name)

if __name__ == '__main__':
    # Example usage (optional, for testing FontManager directly)
    # This requires a CTk App to be running to actually create fonts and accurately test fallbacks.
    # For simplicity, we'll just check if the class can be instantiated and fonts retrieved.
    print("Attempting to initialize FontManager...")
    try:
        # To test CTkFont creation properly, a root window usually needs to exist.
        # We'll create a dummy one for this test block if customtkinter is available.
        try:
            root = ctk.CTk() 
            root.withdraw() # Hide the dummy window
            print("Dummy CTk root created for font testing.")
        except Exception as e:
            print(f"Could not create dummy CTk root, font creation might be limited: {e}")
            # If CTk cannot be initialized (e.g. no display), this test is still valuable
            # for checking the class logic itself, even if real fonts aren't created.

        fm = FontManager()
        print("FontManager initialized.")

        font_style_to_test = "header_20_bold"
        font = fm.get_font(font_style_to_test)
        
        if font:
            # Note: .cget() might not work as expected if no root window is present for CTkFont
            # We will print the object itself, and if possible, its properties.
            print(f"Successfully retrieved font object for style '{font_style_to_test}': {font}")
            try:
                print(f"  Family: {font.cget('family')}")
                print(f"  Size: {font.cget('size')}")
                print(f"  Weight: {font.cget('weight')}")
            except Exception as e:
                print(f"  Could not cget font properties (likely no CTk root or display): {e}")
        else:
            print(f"Font style '{font_style_to_test}' not found.")
        
        non_existent_font_style = "random_style_123"
        non_existent_font = fm.get_font(non_existent_font_style)
        if non_existent_font is None:
            print(f"Successfully handled request for non-existent font style '{non_existent_font_style}'.")
        else:
            print(f"Error: Non-existent font style '{non_existent_font_style}' returned an object: {non_existent_font}")

        # Clean up dummy root if it was created
        try:
            if 'root' in locals() and root:
                root.destroy()
                print("Dummy CTk root destroyed.")
        except Exception as e:
            print(f"Error destroying dummy CTk root: {e}")


    except ImportError:
        print("ImportError: customtkinter is not available. Cannot run FontManager tests that depend on it.")
    except Exception as e:
        # This will catch errors during FontManager instantiation or font creation if CTk is present but fails.
        print(f"Error during FontManager test: {e}")
    finally:
        print("FontManager test finished.")
