import ctypes
from ctypes import wintypes
import time

# This script attempts to set the audio output to your Bluetooth headset
# using Windows Core Audio APIs

def set_default_audio_endpoint(device_name_substring):
    """
    Attempt to set the default audio endpoint to a device containing the substring
    """
    try:
        # Import the required Windows libraries
        import comtypes
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
        
        # Get all audio devices
        devices = AudioUtilities.GetAllSessions()
        
        # Try to find and set the default device
        # For this to work properly, we'd need pycaw and comtypes installed
        print(f"Looking for audio device containing: {device_name_substring}")
        
        # Get the default audio device
        default_device = AudioUtilities.GetSpeakers()
        if default_device:
            print("Found default audio device")
            # Try to switch to the Bluetooth device
            # This requires enumerating audio endpoints
        else:
            print("Could not access default audio device")
            
    except ImportError:
        print("Required audio libraries not available")
        print("You may need to install pycaw: pip install pycairo pycaw")
    except Exception as e:
        print(f"Error setting audio device: {e}")

def test_audio_with_pygame():
    """
    Try to play audio using pygame which may respect current audio settings
    """
    try:
        import pygame
        import os
        
        pygame.mixer.init()
        
        # Look for our TTS audio files
        tts_dirs = []
        import tempfile
        import os
        temp_dir = tempfile.gettempdir()
        
        # Find recent TTS files
        import glob
        tts_files = glob.glob(os.path.join(temp_dir, "tts-*", "voice-*.mp3"))
        
        if tts_files:
            # Get the most recent file
            latest_file = max(tts_files, key=os.path.getctime)
            print(f"Attempting to play: {latest_file}")
            
            if os.path.exists(latest_file):
                pygame.mixer.music.load(latest_file)
                pygame.mixer.music.play()
                
                # Wait for playback
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                print("Audio playback completed")
            else:
                print("Latest TTS file not found")
        else:
            print("No TTS files found in temp directory")
            
    except ImportError:
        print("Pygame not available")
    except Exception as e:
        print(f"Error in pygame audio: {e}")

if __name__ == "__main__":
    print("Setting audio output to Force of Nature headset...")
    set_default_audio_endpoint("Force of Nature")
    
    print("\nTesting audio playback...")
    test_audio_with_pygame()
    
    print("\nIf you didn't hear the audio, try:")
    print("1. Manually setting 'Force of Nature' as default in Windows audio settings")
    print("2. Restarting Windows Audio service again")
    print("3. Using a different audio player to test")