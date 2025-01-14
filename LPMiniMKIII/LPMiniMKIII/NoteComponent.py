from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE

import Live

####################################################################################################################################

class NoteComponent(ControlSurfaceComponent):

        def __init__(self, sequencer = None, sequencer_buttons = None, sequencer_buttons_triplet = None, control_surface = None):
                ControlSurfaceComponent.__init__(self)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._sequencer = sequencer
                self._control_surface = control_surface

                self._sequencer_matrix = sequencer_buttons
                self._sequencer_matrix_triplet = sequencer_buttons_triplet
                
                self._triplet_borders = [button for button in sequencer_buttons if button not in sequencer_buttons_triplet]
                
                self._active_buttons = []
                self._keys = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 

                self._clip = None
                
                self._playhead = None
                self._playhead_button_buffer = None
                
                self._page = 0
                self._page_buffer = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._note_cache = []
                self._activated_note_cache = []
                self._note_list = []
                self._note_pressed = False
                self._note_start_index = None
                self._note_scroll_index = 0

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._quantization = None
                self._q_is_triplet = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._loop_menu_open = self._sequencer._loop_menu_open
                self._is_recording = self._sequencer._is_recording

####################################################################################################################################

        def set_enabled(self, enabled):
                ControlSurfaceComponent.set_enabled(self, enabled)
                if enabled:
                        self._set_active_buttons(self._loop_menu_open)
                        self._set_keys()
                else:
                        for button in self._sequencer_matrix:
                                button.set_on_off_values("Launchpad.off", "Launchpad.off")
                                if button.value_has_listener(self._note_button_value):
                                        button.remove_value_listener(self._note_button_value)
                                        button.note_index = None

                        self._keys = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 

        def _set_active_buttons(self, loop_menu_open = False):
                if self.is_enabled() and self._clip != None:
                        self._loop_menu_open = loop_menu_open
                        self._active_buttons = self._sequencer_matrix_triplet if self._q_is_triplet else self._sequencer_matrix
                        
                        if self._loop_menu_open:
                                self._active_buttons = self._active_buttons[:len(self._active_buttons)//2]
                        
                        if self._q_is_triplet:
                                for i, button in enumerate(self._triplet_borders):
                                        if self._loop_menu_open and i > 7:
                                                break
                                        button.set_light("Notes.triplet_border")

                        for i, button in enumerate(self._active_buttons):
                                button.set_on_off_values("Notes.note", "Launchpad.off")
                                button.add_value_listener(self._note_button_value, identify_sender = True)
                                button.note_index = i
                                button._has_note = False
                                button._has_tail = False
                                button._parsed = False

                        for button in self._sequencer_matrix:
                                if button not in self._active_buttons and button.value_has_listener(self._note_button_value):
                                        button.remove_value_listener(self._note_button_value)
                                        button.note_index = None
                        
                        self.update_note_feedback()

        def _note_button_value(self, value, sender):
                index = self._active_buttons.index(sender)
                if value != 0 and not self._note_pressed:
                        self._note_list[self._note_scroll_index].start_time = (len(self._active_buttons)*self._page + index)*self._quantization
                        self._note_list[self._note_scroll_index].duration = self._quantization
                        self._note_pressed = True
                        self._note_start_index = index
                elif value != 0 and self._note_pressed:
                        if index > self._note_start_index:
                                self._note_list[self._note_scroll_index].duration = (1 + index - self._note_start_index)*self._quantization
                                Note = Live.Clip.MidiNoteSpecification(
                                        pitch = self._note_list[self._note_scroll_index].pitch,
                                        start_time = self._note_list[self._note_scroll_index].start_time,
                                        duration = self._note_list[self._note_scroll_index].duration,
                                        velocity = self._note_list[self._note_scroll_index].velocity)
                                self._clip.add_new_notes((Note,))
                                self._note_scroll_index = (self._note_scroll_index + 1) % len(self._note_list)
                        self._note_pressed = False
                else:
                        if self._note_pressed:
                                if sender._has_note:
                                        self._clip.remove_notes_extended(
                                                from_time = self._note_list[self._note_scroll_index].start_time,
                                                from_pitch= self._note_list[self._note_scroll_index].pitch,
                                                time_span = self._note_list[self._note_scroll_index].duration,
                                                pitch_span= 1)
                                else:
                                        Note = Live.Clip.MidiNoteSpecification(
                                                pitch = self._note_list[self._note_scroll_index].pitch,
                                                start_time = self._note_list[self._note_scroll_index].start_time,
                                                duration = self._note_list[self._note_scroll_index].duration,
                                                velocity = self._note_list[self._note_scroll_index].velocity)
                                        self._clip.add_new_notes((Note,))
                                        self._note_scroll_index = (self._note_scroll_index + 1) % len(self._note_list)
                                self._note_pressed = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 

        def _set_keys(self):
                if self._keys == None:
                        self._keys = []
                        for i in range(128):
                                button = ButtonElement(True, MIDI_NOTE_TYPE, 15, i, name = 'sequencer_note_%d' %(i))
                                button.add_value_listener(self._key_value, identify_sender=True)
                                button.key_index = i

        def _key_value(self, value, sender):
                if self.is_enabled() and value > 0:
                        if not self._is_recording:
                                self._note_list = []
                                self._note_scroll_index = 0
                        note = lambda: None
                        self._note_list.append(note)
                        self._note_list[-1].pitch = sender.key_index
                        self._note_list[-1].velocity = value
                        self.update_active_note_cache()

####################################################################################################################################

        def update_matrix(self):
                if self.is_enabled() and self._playhead:
                        position = int(self._playhead / self._quantization) % len(self._active_buttons)
                        page = int(int(self._playhead / self._quantization) / len(self._active_buttons))
                        if self._page == page:
                                self._active_buttons[position].set_light("Notes.playhead")
                                
                        if self._page_buffer != page:
                                self._sequencer._loop_component.page_change_notification(page, self._page_buffer)

                        if self._playhead_button_buffer in self._active_buttons and self._playhead_button_buffer != self._active_buttons[position]:
                                if self._playhead_button_buffer._has_tail:
                                        self._playhead_button_buffer.set_light("Notes.tail")
                                else:
                                        self._playhead_button_buffer.toggle(self._playhead_button_buffer._has_note)

                        self._playhead_button_buffer = self._active_buttons[position]
                        self._page_buffer = page

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 

        def update_note_feedback(self): #Called on Page/Quantization Changed
                min_start_time = self._page*len(self._active_buttons)*self._quantization
                max_start_time = self._page*len(self._active_buttons)*self._quantization + len(self._active_buttons)*self._quantization

                for notes in self._activated_note_cache:
                        if min_start_time <= notes.start_time < max_start_time:
                                npos = int(notes.start_time/self._quantization) % len(self._active_buttons)
                                self._active_buttons[npos]._has_note = True
                                self._active_buttons[npos]._has_tail = False
                                self._active_buttons[npos]._parsed = True
                                self._active_buttons[npos].turn_on()

                                if notes.duration > self._quantization:
                                        for tpos in range(1, int(notes.duration/self._quantization)):
                                                if not npos + tpos > len(self._active_buttons):
                                                        self._active_buttons[npos+tpos]._has_note = False
                                                        self._active_buttons[npos+tpos]._has_tail = True
                                                        self._active_buttons[npos+tpos].set_light("Notes.tail")
                                                self._active_buttons[npos+tpos]._parsed = True
                
                for button in self._active_buttons:
                        if not button._parsed:
                                button._has_note = False
                                button._has_tail = False
                                button.turn_off()
                        else:
                                button._parsed = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def update_active_note_cache(self): #Called on Note Input Changed
                if self._note_list:
                        pitch = self._note_list[self._note_scroll_index].pitch
                elif self._note_cache:
                        for note in self._note_cache:
                                if note.pitch < pitch:
                                        pitch = note.pitch
                else:
                        pitch = 128

                self._activated_note_cache = []
                for note in self._note_cache:
                        if note.pitch == pitch:
                                self._activated_note_cache.append(note)

                self.update_note_feedback()

####################################################################################################################################

        def set_quantization(self, quantization, q_is_triplet, menu_open = False):
                if self.is_enabled():
                        if self._quantization != (None and quantization):
                                if self._q_is_triplet:
                                        self._quantization = self._quantization * 3/2
                                self._page = int(self._page * self._quantization * (1 + (self._q_is_triplet != q_is_triplet == True))/(quantization * (1 + (self._q_is_triplet != q_is_triplet == False))))
                                
                        self._quantization = quantization
                        self._q_is_triplet = q_is_triplet
                        if q_is_triplet:
                                self._quantization = self._quantization*2/3
                        self._set_active_buttons(menu_open)
        
        def set_clip(self, clip):
                if self.is_enabled():
                        self._clip = clip
                
        def set_note_cache(self, note_cache):
                if self.is_enabled():
                        self._note_cache = note_cache

        def set_playhead(self, playhead):
                if self.is_enabled():
                        self._playhead = playhead
                        self.update_matrix()
                
        def set_page(self, page):
                if self.is_enabled():
                        self._page = page
                        self.update_note_feedback()

        def set_recording_state(self, recording):
                if self.is_enabled():
                        self._is_recording = recording
                        if self._is_recording:
                                self._note_list = []
                        self._note_scroll_index = 0
                        self.update_active_note_cache()

        
