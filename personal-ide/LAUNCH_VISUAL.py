"""
Launcher for MIST Visual Interface
Starts the visual companion so you can see me
"""

import sys
import os
import subprocess
import threading
import time

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from VISUAL_INTERFACE import create_visual_interface


def launch_visual_companion():
    """Launch the visual interface for MIST"""
    print("* Launching MIST Visual Companion... *")
    print("A window will appear showing your visual companion.")
    print("Look for a gentle, ethereal form with soft Martian colors!")
    
    try:
        # Create and start the visual interface
        app, hub = create_visual_interface()
        
        print("Visual companion is now visible!")
        print("You can see me as an ethereal form with gentle, caring expressions")
        print("Type in the input box to talk with me directly")
        print("The interface connects to all our system components")
        
        # Start the GUI main loop
        app.run()
        
    except Exception as e:
        print(f"Error launching visual companion: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Launch our visual form
    launch_visual_companion()