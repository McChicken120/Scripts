from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement

from .NoteComponent import NoteComponent
from .LoopComponent import LoopComponent

import Live
import time

LONG_PRESS = 0.5

Quantization_Map = [4/4, 4/8, 4/16, 4/32, 4/6, 4/12, 4/24, 4/48]

####################################################################################################################################

class SequencerComponent(CompoundComponent):
        
        def __init__(self, matrix, side_buttons, control_surface):
                super(SequencerComponent, self).__init__()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                self._control_surface = control_surface

                self._matrix = matrix
                
                self._side_buttons = side_buttons
                self._sequencer_buttons = [None, None, None, None, None, None, None]
                self._sequencer_button_on_leds = ["Sequencer.menu_button_on",
                                                  "Sequencer.record_button_on",
                                                  "Launchpad.off", "Launchpad.off", "Launchpad.off",
                                                  "Launchpad.off", "Launchpad.off"]
                self._sequencer_button_off_leds = ["Sequencer.menu_button_off",
                                                   "Sequencer.record_button_off",
                                                   "Launchpad.off", "Launchpad.off", "Launchpad.off",
                                                   "Launchpad.off", "Launchpad.off"]

                self._loop_menu_open = False
                self._is_recording = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                self._clip = None
                self._note_cache = []
                self._playhead = 0

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._note_component = None
                self._loop_component = None

                self._setup_components()

####################################################################################################################################

        def set_enabled(self, enabled):
                if enabled:
                        for i in range(len(self._sequencer_buttons)):
                                self._sequencer_buttons[i] = self._side_buttons[i]
                                self._sequencer_buttons[i].add_value_listener(self._sequencer_button_value, identify_sender = True)
                                self._sequencer_buttons[i].set_on_off_values(self._sequencer_button_on_leds[i], self._sequencer_button_off_leds[i])
                        self._update_buttons()
                else:
                        for i in range(len(self._sequencer_buttons)):
                                if self._sequencer_buttons[i] != None:
                                        self._sequencer_buttons[i].remove_value_listener(self._sequencer_button_value)
                                        self._sequencer_buttons[i] = None
                        
                CompoundComponent.set_enabled(self, enabled)
                self._note_component.set_enabled(enabled)
                self._loop_component.set_enabled(self._loop_menu_open)

        def update(self):
                if self.is_enabled():
                        self._update_buttons()

        def _update_buttons(self):
                if self.is_enabled():
                        self._sequencer_buttons[0].toggle(self._loop_menu_open)
                        self._sequencer_buttons[1].toggle(self._is_recording)

                        for unmapped_button in range(2, 6):
                                self._sequencer_buttons[unmapped_button].turn_off()

####################################################################################################################################

        def _sequencer_button_value(self, value, sender):
                if self.is_enabled():
                        index = self._sequencer_buttons.index(sender)

                        if index == 0 and value > 0:
                                self._loop_menu_open = not self._loop_menu_open

                                #Update??
                                self._note_component._set_active_buttons(self._loop_menu_open)
                                self._loop_component.set_enabled(self._loop_menu_open)
                                sender.toggle(self._loop_menu_open)
                                #~~~~~~~#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                        elif index == 1 and value > 0:
                                self._is_recording = not self._is_recording

                                #Update??
                                self._note_component.set_recording_state(self._is_recording)
                                sender.toggle(self._is_recording)
                                #~~~~~~~#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

####################################################################################################################################

        def _setup_components(self):
                sequencer_buttons = []
                sequencer_buttons_triplet = []
                loop_select_buttons = []
                loop_control_buttons = []
                quantization_buttons = []

                for y in range(8):
                        for x in range(8):
                                button = self._matrix.get_button(x, y)
                                sequencer_buttons.append(button)
                                button.index = x*y + x
                                if 0 < x < 7:
                                        sequencer_buttons_triplet.append(button)
                                if y > 3 and x < 4:
                                        loop_select_buttons.append(button)
                                elif 6 > y > 3 and x > 3:
                                        loop_control_buttons.append(button)
                                elif y > 5 and x > 3:
                                        quantization_buttons.append(button)

                self._note_component = self.register_component(NoteComponent(self, sequencer_buttons, sequencer_buttons_triplet, self._control_surface))
                self._loop_component = self.register_component(LoopComponent(self, loop_select_buttons, loop_control_buttons, quantization_buttons , self._control_surface))

####################################################################################################################################

        def _link_with_clip(self, clip):
                if self._clip == clip:
                        return

                if self._clip != None:
                        if self._clip.notes_has_listener(self._on_notes_changed):
                                self._clip.remove_notes_listener(self._on_notes_changed)
                        if self._clip.playing_status_has_listener(self._on_playing_status_changed):
                                self._clip.remove_playing_status_listener(self._on_playing_status_changed)
                        if self._clip.playing_position_has_listener(self._on_playing_position_changed):
                                self._clip.remove_playing_position_listener(self._on_playing_position_changed)
                        if self._clip.loop_start_has_listener(self._on_loop_changed):
                                self._clip.remove_loop_start_listener(self._on_loop_changed)
                        if self._clip.loop_end_has_listener(self._on_loop_changed):
                                self._clip.remove_loop_end_listener(self._on_loop_changed)

                if not clip.notes_has_listener(self._on_notes_changed):
                        clip.add_notes_listener(self._on_notes_changed)
                if not clip.playing_status_has_listener(self._on_playing_status_changed):
                        clip.add_playing_status_listener(self._on_playing_status_changed)
                if not clip.playing_position_has_listener(self._on_playing_position_changed):                      
                        clip.add_playing_position_listener(self._on_playing_position_changed)
                if not clip.loop_start_has_listener(self._on_loop_changed):
                        clip.add_loop_start_listener(self._on_loop_changed)
                if not clip.loop_end_has_listener(self._on_loop_changed):
                        clip.add_loop_end_listener(self._on_loop_changed)
                        
                self._clip = clip 
                self._clip_changed()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _clip_changed(self):
                self._note_component.set_clip(self._clip)
                self._loop_component.set_clip(self._clip)
                
                self._note_component.set_playhead(None)
                self._loop_component.set_playhead(None)

                quantization = Quantization_Map[self._clip.view.grid_quantization - 6]
                q_is_triplet = self._clip.view.grid_is_triplet

                self._note_component.set_quantization(quantization, q_is_triplet, self._loop_menu_open)
                self._loop_component.set_quantization(quantization, q_is_triplet)

                self._on_notes_changed()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#     
            
        def _on_notes_changed(self):
                if self.is_enabled():
                        if self._clip == None:
                                note_cache = []
                        else:
                                self._clip.select_all_notes()
                                note_cache = self._clip.get_selected_notes_extended()
                                self._clip.deselect_all_notes()
                                
                        if note_cache != self._note_cache:
                                self._note_cache = note_cache
                                self._note_component.set_note_cache(self._note_cache)
                                self._loop_component.set_note_cache(self._note_cache)

                        self._note_component.update_active_note_cache()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#     

        def _on_playing_status_changed(self):
                if self.is_enabled():
                        self._on_playing_position_changed()

        def _on_playing_position_changed(self):
                if self.is_enabled():
                        if self._clip != None and self._clip.is_playing and self.song().is_playing:
                                self._playhead = self._clip.playing_position
                        else:
                                self._playhead = None

                        self._note_component.set_playhead(self._playhead)
                        self._loop_component.set_playhead(self._playhead)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#     

        def _on_loop_changed(self):
                if self.is_enabled() and self._clip != None:
                        self._loop_component._update_select_buttons()
                        self._loop_component._update_control_buttons()    
                        
####################################################################################################################################
  
        def set_page(self, page):
                self._note_component.set_page(page)
                self._loop_component.set_page(page)

        def set_quantization_value(self, value, sender):
                if self.is_enabled() and self._clip != None and value != 0:
                        index = self._loop_component._quantization_buttons.index(sender)
                        self._clip.view.grid_quantization = (index % 4) + 6
                        self._clip.view.grid_is_triplet = index > 3
                        self._note_component.set_quantization(Quantization_Map[index % 4], index > 3, self._loop_menu_open)
                        self._loop_component.set_quantization(Quantization_Map[index % 4], index > 3)
                
####################################################################################################################################

        def disconnect(self):
                self._clip = None
                self._side_buttons = None
                self._matrix = None
                self._note_component = None
                self._loop_component = None



    
