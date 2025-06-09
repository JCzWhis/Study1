import argparse
import sys
import logging # Added to allow direct use of logging.getLogger() for level setting

# Import utilities
from utils.config import get_config
from utils.logging import get_logger # This will also call setup_logging()
from utils.diagnostics import perform_system_diagnostics
from ui.main_window import MainWindow

# Initialize logger for main module
# Logging is configured when utils.logging is imported
logger = get_logger(__name__)

def run_gradio_interface(config, port, debug_mode):
    logger.info(f"Attempting to launch Gradio interface on port {port} (Debug: {debug_mode})...")
    # Placeholder: Actual Gradio app import and launch will go here
    # Example:
    # from interfaces.gradio_app import create_app
    # app = create_app(config) # Pass the loaded config
    # app.launch(server_name="0.0.0.0", server_port=port, debug=debug_mode)
    logger.info("Placeholder: Gradio interface would start here.")
    logger.info("To run Gradio, you would typically import your Gradio app and call app.launch()")

def run_tkinter_interface(config, debug_mode):
    logger.info(f"Attempting to launch Tkinter interface (Debug: {debug_mode})...")
    # Placeholder: Actual Tkinter app import and launch will go here
    # Example:
    # from interfaces.tkinter_app import App
    # app = App(config) # Pass the loaded config
    # app.mainloop()
    logger.info("Launching CustomTkinter interface...")
    app = MainWindow(config=config)
    app.mainloop()
    logger.info("CustomTkinter interface closed.")

def auto_detect_interface():
    logger.info("Attempting to auto-detect best available interface...")
    # Basic detection logic (can be expanded)
    # For now, prefers Gradio if available, otherwise Tkinter
    try:
        import gradio
        logger.info("Gradio detected.")
        return "gradio"
    except ImportError:
        logger.info("Gradio not found.")
    try:
        import customtkinter # or tkinter
        logger.info("CustomTkinter (or Tkinter) detected.")
        return "tkinter"
    except ImportError:
        logger.info("CustomTkinter (or Tkinter) not found.")

    logger.error("No suitable GUI interface libraries detected by auto-detection.")
    return None

def main():
    # Load configuration first
    config = get_config()
    app_config = config.get('App', {}) # Get the 'App' section, or empty dict if not found

    parser = argparse.ArgumentParser(description="MedStudy Pro - Medical Study Assistant")
    parser.add_argument(
        "--interface",
        choices=["gradio", "tkinter", "auto"],
        default=app_config.get("default_interface", "auto"), # Default from config
        help="Specify the interface to use (gradio, tkinter, or auto-detect)."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(app_config.get("default_port", 7860)), # Default from config, ensure int
        help="Port number for the Gradio web interface."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        # default value is derived below to correctly prioritize command-line flag
        help="Enable debug mode (overrides config if specified)."
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Run system diagnostics and exit."
    )

    args = parser.parse_args()

    # Determine effective debug mode: command line flag > config file > default False
    if args.debug: # Command line flag takes precedence
        current_debug_mode = True
    else: # Otherwise, use config or fallback to False
        current_debug_mode = app_config.get("debug_mode", False)

    # Update logger level if debug mode changed dynamically
    if current_debug_mode:
        # Ensure this is done after initial logging setup by utils.logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug(f"Debug mode is ON. Initial config value was: {app_config.get('debug_mode', False)}, CLI flag: {args.debug}")
    else:
        logging.getLogger().setLevel(logging.INFO) # Explicitly set to INFO if not debug
        logger.debug(f"Debug mode is OFF. Initial config value was: {app_config.get('debug_mode', False)}, CLI flag: {args.debug}")


    if args.diagnostic:
        logger.info("Diagnostic mode selected. Running system diagnostics...")
        all_ok = perform_system_diagnostics()
        sys.exit(0 if all_ok else 1) # Exit with 0 if all ok, 1 if issues

    interface_choice = args.interface
    port_choice = args.port

    if interface_choice == "auto":
        logger.info("Auto-detecting interface...")
        detected_interface = auto_detect_interface()
        if detected_interface:
            interface_choice = detected_interface
            logger.info(f"Auto-detected interface: {interface_choice}")
        else:
            logger.error("Error: Could not auto-detect a suitable interface. Please install Gradio or CustomTkinter.")
            logger.info("You can try running with --interface gradio or --interface tkinter if you believe one is installed.")
            sys.exit(1)

    logger.info(f"Selected interface: {interface_choice}")
    logger.info(f"Debug mode active: {current_debug_mode}")

    if interface_choice == "gradio":
        run_gradio_interface(config, port_choice, current_debug_mode)
    elif interface_choice == "tkinter":
        run_tkinter_interface(config, current_debug_mode)
    else:
        logger.error(f"Error: Unknown or unselected interface '{interface_choice}'.")
        sys.exit(1)

if __name__ == "__main__":
    # Initial message before logging might be fully set if utils are slow to import
    # print("MedStudy Pro Launcher - Initializing...")
    # Logger will print its own init messages once utils.logging is imported.
    main()
