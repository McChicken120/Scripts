from _Framework.ControlSurface import ControlSurface

from _Framework.ButtonMatrixElement import ButtonMatrixElement
#from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE

from .ConfigurableButtonElement import ConfigurableButtonElement
from .MainSelectorComponent import MainSelectorComponent
from .Skin import make_skin

from .SYSEX_MESSAGES import *

import Live
import time

####################################################################################################################################

class Launchpad(ControlSurface):
        
        def __init__(self, c_instance):
                ControlSurface.__init__(self, c_instance)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._send_midi(SYSEX_HEADER + SYSEX_PARAMETERS['Startup'] + SYSEX_END)
                self._send_midi(SYSEX_HEADER + SYSEX_PARAMETERS['Clear_All'] + SYSEX_END)
                self._send_midi(SYSEX_HEADER + SYSEX_PARAMETERS['Default'] + SYSEX_END)

                self._c_instance = c_instance

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._skin = make_skin()
                self._side_notes = (89, 79, 69, 59, 49, 39, 29)
                self._selector = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self.song().master_track.add_data_listener(self._sysex_feedback_update)
                self._sysex_led_message = ()
                
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._undo_mode = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                with self.component_guard():
                        self._setup_components()

####################################################################################################################################      

        def _setup_components(self):
                
                top_buttons = [ConfigurableButtonElement(True, MIDI_CC_TYPE, 0, 91 + index, name = ('Top_Button_%d' % index), skin = self._skin) for index in range(8)]
                side_buttons = [ConfigurableButtonElement(True, MIDI_CC_TYPE, 0, self._side_notes[index], name = ('Side_Button_%d' % index), skin = self._skin) for index in range(7)]
                
                undo_button = ConfigurableButtonElement(True, MIDI_CC_TYPE, 0, 19, name = 'Undo_Button', skin = self._skin)
                undo_button.set_on_off_values("Launchpad.redo_button", "Launchpad.undo_button")
                undo_button.add_value_listener(self.undo, identify_sender = True)
                undo_button.toggle(self._undo_mode)

                matrix = ButtonMatrixElement()
                matrix.name = 'Button_Matrix'
                
                for y in range(7, -1, -1):
                        row = []
                        for x in range(8):
                                note = 11 + (10*y) + x
                                button = ConfigurableButtonElement(True, MIDI_NOTE_TYPE, 0, note, skin = self._skin)
                                button.x_index = x
                                button.y_index = abs(7 - y)
                                button.note = note
                                
                                row.append(button)
                        matrix.add_row(row)
                        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._selector = MainSelectorComponent(matrix, tuple(top_buttons), tuple(side_buttons), self, self._c_instance)

####################################################################################################################################

        def undo(self, value, sender):
                now = time.time()
                if value != 0:
                        self._last_action = now
                else:
                        if now - self._last_action < LONG_PRESS:
                                if not self._undo_mode and self.song().can_undo:
                                        self.song().undo()
                        elif self._undo_mode and self.song().can_redo:
                                self.song().redo()
                        else:
                                self._undo_mode = not self._undo_mode
                                sender.toggle(self._undo_mode)

####################################################################################################################################

        def _sysex_feedback_update(self):
                if self.song().master_track.get_data('Logo_Update', False):
                        self._queue_led_sysex(99, self.song().master_track.get_data('Logo_Color', ()))
                        self.song().master_track.set_data('Logo_Update', False)

                if self.song().master_track.get_data('Display_Faders', -1):
                        data = self.song().master_track.get_data('Display_Faders', -1)
                        if data in (5, 6):
                                for i, track in enumerate(self.song().tracks if data == 5 else self.song().return_tracks):
                                        num_buttons = int(((track.mixer_device.volume.value * 127) + 1) / 16)
                                        for b in range(num_buttons):
                                                self._queue_led_sysex((3,) + (((10 * (b+1)) + (i+1)),) + TRACK_COLORS[track.color_index])
                        self.song().master_track.set_data('Display_Faders', 0)

                if self._sysex_led_message:
                        self._send_midi(SYSEX_HEADER + SYSEX_PARAMETERS['Set_LEDs'] + self._sysex_led_message + SYSEX_END)
                        self.log_message("Sysex Message Sent: " + str(SYSEX_HEADER + SYSEX_PARAMETERS['Set_LEDs'] + self._sysex_led_message + SYSEX_END))
                        self._sysex_led_message = ()
                

        def _queue_led_sysex(self, message):
                self._sysex_led_message = self._sysex_led_message + message


        def disconnect(self):
                self._send_midi(SYSEX_HEADER + (0, 0) + SYSEX_END)
                self._send_midi(SYSEX_HEADER + SYSEX_PARAMETERS['Startup'] + SYSEX_END)


        

                        



