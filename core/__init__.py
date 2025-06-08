# Make key components available directly under the core namespace
# Example: from core import LLMManager

# Note: These imports will only work once the respective files and classes are created.
# If you see ImportError, it's likely because the submodule or class doesn't exist yet.

try:
    from .llm_manager import LLMManager
except ImportError:
    # This allows the package to be imported even if submodules are not yet created
    # You might want to log a warning here or handle it differently in a production system
    pass

try:
    from .anki_system import AnkiSystem
except ImportError:
    pass

try:
    from .rag_engine import RAGEngine
except ImportError:
    pass

# You can also define package-level variables or functions here if needed.
__all__ = ['LLMManager', 'AnkiSystem', 'RAGEngine']

print("Core package loaded. Submodule import status can be checked if necessary.")
