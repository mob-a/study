
import sys
import os
import datetime

import pyauto
from keyhac import *


def configure(keymap):
 keymap_global = keymap.defineWindowKeymap()
 keymap_global[ "C-X" ] = keymap.defineMultiStrokeKeymap("C-X")

 if 1:
        keymap_global[ "C-P" ] = "Up"                  # Move cursor up
        keymap_global[ "C-N" ] = "Down"                # Move cursor down
        keymap_global[ "C-F" ] = "Right"               # Move cursor right
        keymap_global[ "C-B" ] = "Left"                # Move cursor left
        keymap_global[ "C-A" ] = "Home"                # Move to beginning of line
        keymap_global[ "C-E" ] = "End"                 # Move to end of line
        keymap_global[ "A-F" ] = "C-Right"             # Word right
        keymap_global[ "A-B" ] = "C-Left"              # Word left
        keymap_global[ "C-V" ] = "PageDown"            # Page down
        keymap_global[ "A-V" ] = "PageUp"              # page up
        keymap_global[ "A-Comma" ] = "C-Home"          # Beginning of the document
        keymap_global[ "A-Period" ] = "C-End"          # End of the document
        keymap_global[ "C-X" ][ "C-F" ] = "C-O"        # Open file
        keymap_global[ "C-X" ][ "C-S" ] = "C-S"        # Save
        keymap_global[ "C-X" ][ "C-W" ] = "A-F","A-A"  # Save as
        keymap_global[ "C-X" ][ "U" ] = "C-Z"          # Undo
        keymap_global[ "C-S" ] = "C-F"                 # Search
        keymap_global[ "A-X" ] = "C-G"                 # Jump to specified line number
        keymap_global[ "C-X" ][ "H" ] = "C-A"          # Select all
        keymap_global[ "C-W" ] = "C-X"                 # Cut
        keymap_global[ "A-W" ] = "C-C"                 # Copy
        keymap_global[ "C-Y" ] = "C-V"                 # Paste
      
        keymap_global[ "C-G" ] = "Esc"                 
        keymap_global[ "C-Backslash" ] = "C-Z"                 
        keymap_global[ "C-D" ] = "Delete"     
        keymap_global[ "C-H" ] = "Back" 
        keymap_global[ "C-Space" ] = "S-Down" 
        keymap_global[ "C-A-Space" ] = "S-Up" 
        keymap_global[ "C-K" ] = "S-End","C-X" 
        keymap_global[ "S-A-Comma" ] = "C-Home" 
        keymap_global[ "S-A-Period" ] = "C-End" 

