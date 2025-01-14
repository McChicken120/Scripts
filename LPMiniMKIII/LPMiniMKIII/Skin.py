from _Framework.Skin import Skin
from .Colors import *

####################################################################################################################################

class Colors:
    
    class Launchpad:
        off = empty

        redo_button = green_dark_full
        undo_button = red_full
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    class Selector:
        arrows_on = pink_full
        arrows_off = green_half

        modes_on = purple_full
        modes_off = orange_half
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    class Session:
        
        selected = mint_full
        triggered = yellow_half
        stopped = orange_full
        recording = red_full
        started = green_full

        launch_q_button_on = orange_full
        launch_q_button_off = white_half

        record_q_button_on = orange_full
        record_q_button_off = white_half

        unarmed_tracks_notification = red_full

        track_browser_button_on = orange_full
        track_browser_button_off = white_half

        device_browser_button_on = orange_full
        device_browser_button_off = white_half

        track_faders_on = orange_full
        track_faders_off = blue_bright_thrd

        return_track_faders_on = orange_full
        return_track_faders_off = blue_bright_thrd

    class TrackBrowser:
        
        created = orange_half
        available = green_dark_thrd

    class DeviceBrowser:

        folder_selected = green_dark_full
        folder = orange_half

        item_selected = green_full
        item = blue_dark_half

        return_type = yellow_full
        track_type = white_full

        position_back = red_full
        position_front = green_bright_full

        chain_selected = red_half
        chain = white_half

        track_selected = red_half

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    class Sequencer:
        
        menu_button_on = yellow_full
        menu_button_off = yellow_thrd

        record_button_on = red_full
        record_button_off = white_thrd

    class Notes:

        playhead = green_full
        note = purple_full
        tail = pink_thrd

        triplet_border = red_thrd
        
    class Loops:
        
        playhead = green_full
        selected = white_full

        frame_selection = orange_full

        start_end_selection = yellow_half

        quantization_selection_on = mint_bright_full
        quantization_selection_off = white_thrd

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    class Sampler:
        
        default = orange_thrd

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    class Songtempo:

        diagonal_on = red_full
        diagonal_off = white_full
        
        button_pressed = green_full

        above_halftime = orange_full
        halftime = yellow_full

        above_quartertime = yellow_thrd
        quartertime = green_bright_full

        below_quartertime = red_thrd

####################################################################################################################################

def make_skin():
    return Skin(Colors)
