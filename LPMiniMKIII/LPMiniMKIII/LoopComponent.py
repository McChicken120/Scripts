from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement

Grid_Quantization_Values = ["g_quarter", "g_eighth", "g_sixteenth", "g_thirtysecond"]

####################################################################################################################################

class LoopComponent(ControlSurfaceComponent):

        def __init__(self, sequencer, select_buttons, control_buttons, quantization_buttons, control_surface):
                ControlSurfaceComponent.__init__(self)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._sequencer = sequencer
                self._control_surface = control_surface

                self._select_buttons = select_buttons
                self._control_buttons = control_buttons
                self._quantization_buttons = quantization_buttons
                
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._clip = None
                self._playhead = None
                
                self._page = 0
                self._playing_page = 0
                
                self._copy_page = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._loop_start = 0
                self._loop_end = 0
                self._set_loop_range = False

                self._blocksize = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._notes = None
                self._note_cache = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._quantization = None
                self._q_is_triplet = False

####################################################################################################################################

        def set_enabled(self, enabled):
                ControlSurfaceComponent.set_enabled(self, enabled)
                if enabled:
                        self._set_active_buttons()
                else:
                        for button in self._select_buttons:
                                if button.value_has_listener(self._select_button_value):
                                        button.remove_value_listener(self._select_button_value)
                        for button in self._control_buttons:
                                if button.value_has_listener(self._control_button_value):
                                        button.remove_value_listener(self._control_button_value)
                        for button in self._quantization_buttons:
                                if button.value_has_listener(self._sequencer.set_quantization_value):
                                        button.remove_value_listener(self._sequencer.set_quantization_value)

        def _set_active_buttons(self):
                self._update_select_buttons()
                self._update_control_buttons()
                self._update_quantization_buttons()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _update_select_buttons(self):
                if self.is_enabled() and self._clip != None:
                        self._blocksize = self._quantization * (32 - 16 * self._q_is_triplet)
                        for i, button in enumerate(self._select_buttons):
                                if not button.value_has_listener(self._select_button_value):
                                        button.set_on_off_values("Loops.frame_selection", "Launchpad.off")
                                        button.add_value_listener(self._select_button_value, identify_sender = True)
                                button.toggle(i * self._blocksize - self._loop_start < self._clip.length and i >= int(self._loop_start / self._blocksize))
                                if i == self._playing_page != self._page:
                                        button.set_light("Loops.playhead")
                                if i == self._page:
                                        button.set_light("Loops.selected")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _update_control_buttons(self):
                if self.is_enabled() and self._clip != None:
                        self._loop_start = self._clip.loop_start
                        self._loop_end = self._clip.loop_end
                        for i, button in enumerate(self._control_buttons):
                                if not button.value_has_listener(self._control_button_value):
                                        button.set_on_off_values("Loops.start_end_selection", "Launchpad.off")
                                        button.add_value_listener(self._control_button_value, identify_sender = True)
                                if self._loop_start <= (i * 4) < self._loop_end:
                                        button.turn_on()
                                else:
                                        button.turn_off()
                                        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#                      

        def _update_quantization_buttons(self):
                if self.is_enabled() and self._clip != None:
                        for i, button in enumerate(self._quantization_buttons):
                                if not button.value_has_listener(self._sequencer.set_quantization_value):
                                        button.set_on_off_values("Loops.quantization_selection_on", "Loops.quantization_selection_off")
                                        button.add_value_listener(self._sequencer.set_quantization_value, identify_sender = True)
                                if not self._clip.view.grid_is_triplet and i < 4 and Grid_Quantization_Values[i % 4] == str(self._clip.view.grid_quantization):
                                        button.turn_on()
                                elif self._clip.view.grid_is_triplet and i > 3 and Grid_Quantization_Values[i % 4] == str(self._clip.view.grid_quantization):
                                        button.turn_on()
                                else:
                                        button.turn_off()

####################################################################################################################################

        def _select_button_value(self, value, sender):
                if self.is_enabled() and value != 0 and self._copy_page:
                        self._copy_page = False

                if self.is_enabled() and value != 0:
                        self._copy_page = True
                
                if self.is_enabled() and value == 0 and self._copy_page:
                        index = self._select_buttons.index(sender)
                        self._sequencer.set_page(index)
                        self._copy_page = False
                        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _control_button_value(self, value, sender):
                if self.is_enabled() and value != 0:
                        index = self._control_buttons.index(sender)
                        if not self._set_loop_range:
                                self._loop_start = index * 4
                                self._set_loop_range = True
                        else:
                                self._loop_end = index * 4
                                self._set_loop(self._loop_start, self._loop_end)
                                self._set_loop_range = False
                if self.is_enabled() and value == 0 and self._set_loop_range:
                        self._loop_end = self._loop_start
                        self._set_loop(self._loop_start, self._loop_end)
                        self._set_loop_range = False

        def _set_loop(self, start, end):
                old_start = self._clip.loop_start
                old_end = self._clip.loop_end

                if start > end:
                        start, end = end, start
                self._loop_end = end + 4
                self._loop_start = start
                
                if old_end <= start:
                        self._clip.loop_end = self._loop_end
                        self._clip.loop_start = self._loop_start
                else:
                        self._clip.loop_start = self._loop_start
                        self._clip.loop_end = self._loop_end

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def page_change_notification(self, page, page_buffer):
                if self.is_enabled():
                        if not self._page == page_buffer:
                                self._select_buttons[page_buffer].toggle(page_buffer * self._blocksize - self._loop_start < self._clip.length and page_buffer >= int(self._loop_start / self._blocksize))
                        if not self._page == page:
                                self._playing_page = page
                                self._select_buttons[page].set_light("Loops.playhead")

####################################################################################################################################

        def set_quantization(self, quantization, q_is_triplet):
                if self._quantization != (None and quantization):
                        self._page = int(self._page * self._quantization * (1 + (self._q_is_triplet != q_is_triplet == True))/(quantization * (1 + (self._q_is_triplet != q_is_triplet == False))))
                                
                self._quantization = quantization
                self._q_is_triplet = q_is_triplet
                self._update_select_buttons()
                self._update_quantization_buttons()
                
        def set_clip(self, clip):
                self._clip = clip

        def set_page(self, page):
                self._page = page
                self._update_select_buttons()

        def set_playhead(self, playhead):
                self._playhead = playhead

        def set_note_cache(self, note_cache):
                self._note_cache = note_cache
                
