from _Framework.ModeSelectorComponent import ModeSelectorComponent

from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonElement import ButtonElement

from _Framework.SceneComponent import SceneComponent
from _Framework.ClipSlotComponent import ClipSlotComponent

from .SpecialSessionComponent import SpecialSessionComponent
from .SequencerComponent import SequencerComponent
from .SamplerComponent import SamplerComponent
from .SongTempoComponent import SongTempoComponent

import Live

####################################################################################################################################

class MainSelectorComponent(ModeSelectorComponent):
        
        def __init__(self, matrix, top_buttons, side_buttons, control_surface, c_instance):
                ModeSelectorComponent.__init__(self)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                self._control_surface = control_surface
                self._c_instance = c_instance

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._matrix = matrix
                
                self._nav_buttons = top_buttons[:4]
                
                self._mode_buttons = top_buttons[4:]        
                
                self._side_buttons = side_buttons

                self._all_buttons = []

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                                    
                self._session = SpecialSessionComponent(matrix, matrix.width(), matrix.height(), self._side_buttons, c_instance, control_surface, c_instance.song()) #+Variables?
                self._session.name = 'Session_Control'

                self._sequencer = SequencerComponent(matrix, self._side_buttons, c_instance) #+Variables?
                self._sequencer.name = 'Sequencer_Control'

                self._sampler = SamplerComponent(matrix, self._side_buttons, c_instance) #+Variables?
                self._sampler.name = 'Sampler_Control'

                self._songtempo = SongTempoComponent(matrix, self._side_buttons, c_instance) #+Variables?
                self._songtempo.name = 'Song_Tempo_Control'

                self._mode_index = 0

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self.song().add_tracks_listener(self._sequencer_position)
                
                self._sqp = 0           #Sequencer Position
                self._sqp_clip = 0      #Sequencer Clip Position
                self._sqp_library = {}  #Sequencer Position Library
                self._sqp_list = []     #Track Indexer
                
                self._sq_new = True
                self._sequencer_position()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._set_nav_buttons()
                self._set_mode_buttons()
                
                self.update(0)

####################################################################################################################################

        def _set_nav_buttons(self):
                for button in self._nav_buttons:
                        button.set_on_off_values("Selector.arrows_on", "Selector.arrows_off")
                        button.add_value_listener(self._nav_value, identify_sender = True)
                self._update_nav_buttons()

        def _nav_value(self, value, sender):
                if value > 0:
                        index = self._nav_buttons.index(sender)
                        if self._session._session_button_priority[0] != -1 and index < 2:
                                self._session._move_misc_button_row(index)
                        else:
                                clips = max(self._sqp_clips(self._sqp_list[self._sqp]) - 1, 0)
                                if index == 0:                          # UP
                                        if self._sq_new:
                                                self._sq_new = False
                                                self._sqp_clip = clips
                                        elif self._sqp_clip > 0:
                                                self._sqp_clip -= 1
                                if index == 1:                          # DOWN
                                        if self._sqp_clip < clips:      
                                                self._sqp_clip += 1     # clips    = number of clips in track
                                        elif not self._sq_new:          # sqp_clip = selected clip
                                                self._sq_new = True
                                else:
                                        self._sqp += ((2 * index) - 5)
                                self._sqp_update()
                        
        def _update_nav_buttons(self):
                for i, button in enumerate(self._nav_buttons):
                        button.toggle(self._sqp_feedback(i))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _sequencer_position(self):
                #List of Track references
                self._sqp_list = []
                #Go through all tracks in the project
                for position, track in enumerate(self.song().tracks):
                        #Add all unlisted tracks to the library
                        if track.has_midi_input and track.arm:
                                if track not in self._sqp_library:
                                        self._sqp_library[track] = [0, self._sqp_clips(track)]
                                #Update Positions
                                if self._sqp_library[track][0] != position:
                                        self._sqp_library[track][0] = position
                                self._sqp_list.append(track)
                self._sqp_update()

        def _sqp_clips(self, track):
                for i, clipslot in enumerate(track.clip_slots):
                        if not clipslot.has_clip:
                                return i

        def _sqp_update(self):
                if not self._sqp_list:
                        return [0, 0]
                self._sqp = self._sqp % len(self._sqp_list)
                x_index = self._sqp_library[self._sqp_list[self._sqp]][0]
                y_index = self._sqp_library[self._sqp_list[self._sqp]][1] = self._sqp_clips(self._sqp_list[self._sqp])
                if not self._sq_new:
                        y_index = max(min(self._sqp_clip, y_index - 1), 0)
                self._control_surface._set_session_highlight(max(x_index, 0), max(y_index, 0), 1, 1, False)
                self._update_nav_buttons()
                
                                ###########

                #self._c_instance.send_midi((145, self._matrix.get_button(x_index, y_index).note, 121))

                                ###########

                return [x_index, y_index]
                
        def _sqp_feedback(self, index):
                if (index == 0 and (self._sqp_clip > 0 or self._sq_new)) or (index == 1 and not self._sq_new) or (index > 1):
                        return True
                else:
                        return False

####################################################################################################################################

        def _set_mode_buttons(self):
                for button in self._mode_buttons:
                        button.add_value_listener(self._mode_value, identify_sender = True)
                        button.set_on_off_values("Selector.modes_on", "Selector.modes_off")
                self.set_mode(0)
                self._update_mode_buttons()

        def _mode_value(self, value, sender):
                if value == 0:
                        index = self._mode_buttons.index(sender)
                        if self._mode_index != index:
                                self._mode_index = index    
                                self.update(self._mode_index)

        def _update_mode_buttons(self):
                for i, button in enumerate(self._mode_buttons):
                        button.toggle(i == self._mode_index)

####################################################################################################################################

        def update(self, mode = None):
                if self.is_enabled():
                        self._session.set_allow_update(False)
                        if mode == None:
                                mode = self._mode_index
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                        if mode == 0:
                                self._setup_sequencer(False)
                                self._setup_sampler(False)
                                self._setup_songtempo(False)
                                self._setup_session(True)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                        elif mode == 1:
                                self._setup_session(False)
                                self._setup_sampler(False)
                                self._setup_songtempo(False)
                                self._setup_sequencer(True)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                        elif mode == 2:
                                self._setup_session(False)
                                self._setup_sequencer(False)
                                self._setup_songtempo(False)
                                self._setup_sampler(True)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                        elif mode == 3:
                                self._setup_session(False)
                                self._setup_sequencer(False)
                                self._setup_sampler(False)
                                self._setup_songtempo(True)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                        self._session.set_allow_update(True)
                        self._update_mode_buttons()

####################################################################################################################################

        def _setup_session(self, as_active):
                self._session._matrix_changed = as_active
                self._session.set_enabled(as_active)

####################################################################################################################################

        def _setup_sequencer(self, as_active):
                self._sequencer.set_enabled(as_active)
                        
                if as_active:
                        x, y = self._sqp_update()
                        clip_slot = self.song().scenes[y].clip_slots[x]
                        if not clip_slot.has_clip:
                                clip_slot.create_clip(32)
                                clip_slot.clip.view.show_loop()
                                self._sq_new = False
                        if not clip_slot.clip.is_playing:
                                clip_slot.fire()
                                clip_slot.set_fire_button_state(False)
                        self._sequencer._link_with_clip(clip_slot.clip)
                        self.song().view.highlighted_clip_slot = clip_slot
                        self.application().view.show_view('Detail/Clip')

####################################################################################################################################

        def _setup_sampler(self, as_active):
                self._sampler.set_enabled(as_active)

####################################################################################################################################            

        def _setup_songtempo(self, as_active):
                self._songtempo.set_enabled(as_active)

####################################################################################################################################

        def on_enabled_changed(self):
                self.update(self._mode_index)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
        def disconnect(self):
                
                self._matrix = None
                
                self._nav_buttons = None
                self._modes_buttons = None
                
                self._side_buttons = None
                self._session = None
                
                self._sequencer = None
                self._sampler = None
                
                self._songtempo = None
                
                ModeSelectorComponent.disconnect(self)


