import argparse
import sys

# Placeholder for future config loading from config.ini
CONFIG = {
    "default_interface": "auto",
    "default_port": 7860,
    "debug_mode": False,
    "ollama_model": "phi3:mini" # Example, will be loaded from config
}

def run_gradio_interface(port, debug):
    print(f"Attempting to launch Gradio interface on port {port} (Debug: {debug})...")
    # Placeholder: Actual Gradio app import and launch will go here
    # Example:
    # from interfaces.gradio_app import create_app
    # app = create_app(CONFIG)
    # app.launch(server_name="0.0.0.0", server_port=port, debug=debug)
    print("Placeholder: Gradio interface would start here.")
    print("To run Gradio, you would typically import your Gradio app and call app.launch()")

def run_tkinter_interface(debug):
    print(f"Attempting to launch Tkinter interface (Debug: {debug})...")
    # Placeholder: Actual Tkinter app import and launch will go here
    # Example:
    # from interfaces.tkinter_app import App
    # app = App(CONFIG)
    # app.mainloop()
    print("Placeholder: Tkinter interface would start here.")
    print("To run Tkinter, you would typically import your Tkinter app and call app.mainloop()")

def auto_detect_interface():
    print("Attempting to auto-detect best available interface...")
    # Basic detection logic (can be expanded)
    # For now, prefers Gradio if available, otherwise Tkinter
    try:
        import gradio
        print("Gradio detected.")
        return "gradio"
    except ImportError:
        print("Gradio not found.")
    try:
        import customtkinter # or tkinter
        print("CustomTkinter (or Tkinter) detected.")
        return "tkinter"
    except ImportError:
        print("CustomTkinter (or Tkinter) not found.")

    print("No suitable GUI interface libraries detected.")
    return None

def run_diagnostics():
    print("Running system diagnostics...")
    print(f"Python version: {sys.version}")

    # Check Ollama (very basic, can be expanded in utils/diagnostics.py)
    try:
        import requests
        ollama_host = CONFIG.get("ollama_host", "http://localhost:11434")
        print(f"Checking Ollama connection to {ollama_host}...")
        response = requests.get(ollama_host, timeout=5)
        if response.status_code == 200:
            print(f"Ollama connection successful: {response.text.strip()}")
            # Further check for model
            model_name = CONFIG.get("ollama_model", "phi3:mini")
            print(f"Attempting to get info for model: {model_name} (this might take a moment if model needs to be pulled)...")
            # This is a more robust way to check if a model exists with Ollama API
            # response_model_info = requests.post(f"{ollama_host}/api/show", json={"name": model_name}, timeout=30)
            # if response_model_info.status_code == 200:
            #     print(f"Ollama model '{model_name}' is available.")
            # else:
            #     print(f"Warning: Ollama model '{model_name}' not found or Ollama API error. Status: {response_model_info.status_code}")
            #     print(f"You may need to run: ollama pull {model_name}")
            print(f"Simplified model check: For a full check, ensure '{model_name}' is pulled via 'ollama pull {model_name}'.")

        else:
            print(f"Ollama connection failed. Status: {response.status_code}")
            print("Please ensure Ollama is running and accessible.")
    except ImportError:
        print("Warning: 'requests' library not installed. Cannot check Ollama connection.")
        print("Please install it: pip install requests")
    except requests.exceptions.ConnectionError:
        print(f"Ollama connection failed. Could not connect to {ollama_host}.")
        print("Please ensure Ollama is running and accessible.")
    except requests.exceptions.Timeout:
        print(f"Ollama connection timed out when trying to reach {ollama_host}.")

    # Check dependencies (basic)
    print("\nChecking core dependencies:")
    dependencies = ["gradio", "customtkinter", "sentence_transformers", "PyPDF2", "python_docx"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"- {dep}: Installed")
        except ImportError:
            print(f"- {dep}: Not Installed (Warning)")

    print("\nDiagnostics complete. Review warnings if any.")


def main():
    parser = argparse.ArgumentParser(description="MedStudy Pro - Medical Study Assistant")
    parser.add_argument(
        "--interface",
        choices=["gradio", "tkinter", "auto"],
        default=None, # Will use config or auto-detection
        help="Specify the interface to use (gradio, tkinter, or auto-detect)."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None, # Will use config or Gradio default
        help="Port number for the Gradio web interface."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode."
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Run system diagnostics and exit."
    )

    args = parser.parse_args()

    # TODO: Load config from config.ini and update CONFIG dictionary
    # For now, using hardcoded CONFIG merged with args

    current_debug_mode = args.debug or CONFIG.get("debug_mode", False)

    if args.diagnostic:
        run_diagnostics()
        sys.exit(0)

    interface_choice = args.interface if args.interface else CONFIG.get("default_interface", "auto")
    port_choice = args.port if args.port else CONFIG.get("default_port", 7860)

    if interface_choice == "auto":
        detected_interface = auto_detect_interface()
        if detected_interface:
            interface_choice = detected_interface
        else:
            print("Error: Could not auto-detect a suitable interface. Please install Gradio or CustomTkinter.")
            print("You can try running with --interface gradio or --interface tkinter if you believe one is installed.")
            sys.exit(1)

    print(f"Selected interface: {interface_choice}")
    print(f"Debug mode: {current_debug_mode}")

    if interface_choice == "gradio":
        run_gradio_interface(port_choice, current_debug_mode)
    elif interface_choice == "tkinter":
        run_tkinter_interface(current_debug_mode)
    else:
        print(f"Error: Unknown interface '{interface_choice}'.")
        print("This should not happen if auto-detection worked or a valid choice was made.")
        sys.exit(1)

if __name__ == "__main__":
    # print("MedStudy Pro Launcher")
    # print("=====================")
    # print("Note: This is a basic launcher. Full functionality will be built incrementally.")
    # print("Config loading from .ini and full app logic are pending.\n")
    main()
