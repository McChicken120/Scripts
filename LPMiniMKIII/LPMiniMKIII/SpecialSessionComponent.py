from _Framework.SessionComponent import SessionComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.SubjectSlot import subject_slot, subject_slot_group

from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonSliderElement import ButtonSliderElement

from .TrackPresets import *
from .SYSEX_MESSAGES import *

import Live
import time

LONG_PRESS = 0.5

####################################################################################################################################

class SpecialClipSlotComponent(ClipSlotComponent):

        def __init__(self, *a, **k):
                self.parent = None
                self._selected_value = ("Session.selected")
                (super(SpecialClipSlotComponent, self).__init__)(*a, **k)

        def set_parent(self, parent):
                self.parent = parent

        def _feedback_value(self):
                if self._clip_slot == self.song().view.highlighted_clip_slot:
                        return self._selected_value
                else:
                        return ClipSlotComponent._feedback_value(self)

        def _do_select_clip(self, clip_slot):
                super(SpecialClipSlotComponent, self)._do_select_clip(clip_slot)
                if self._clip_slot is not None:
                        if not self.application().view.is_view_visible('Detail/Clip'):
                                self.application().view.show_view('Detail/Clip')
                                        
        @subject_slot('value')
        def _launch_button_value(self, value):
                if self.is_enabled() and self._clip_slot:
                        #Normal Function
                        if self.parent._session_button_priority[0] == -1:
                                self._do_launch_clip(value)
                        #Session Button A - Select Clip
                        elif self.parent._session_button_priority[0] == 0:
                                self._do_select_clip(value)
                        #Session Button B - Copy or Paste Clip
                        elif self.parent._session_button_priority[0] == 1:
                                if not self.has_clip():
                                        if not self.parent._slot_copy_buffer:
                                                self.parent._slot_copy_buffer = self.song().view.highlighted_clip_slot
                                        try:
                                                self.parent._slot_copy_buffer.duplicate_clip_to(self._clip_slot)
                                        except:
                                                pass
                                else: 
                                        self.parent._slot_copy_buffer = self._clip_slot

####################################################################################################################################
    
class SpecialSceneComponent(SceneComponent):
        clip_slot_component_type = SpecialClipSlotComponent

        def __init__(self, *a, **k):
                (super(SpecialSceneComponent, self).__init__)(*a, **k)

####################################################################################################################################

class SpecialSessionComponent(SessionComponent):
        scene_component_type = SpecialSceneComponent

        def __init__(self, matrix, num_tracks, num_scenes, side_buttons, c_instance, control_surface, livesong = None): #Accidentally Breaking Everything (swapped control_surface and c_instance)
                SessionComponent.__init__(self, num_tracks = num_tracks, num_scenes = num_scenes, enable_skinning = True, name='Session', is_root=True)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                self._song = livesong
                self._control_surface = control_surface

                self._matrix = matrix
                self._matrix_changed = False

                self._side_buttons = side_buttons
                self._session_buttons = [None, None, None, None, None, None, None]
                self._session_button_on_leds = ["Session.launch_q_button_on", "Session.record_q_button_on",
                                                "Session.unarmed_tracks_notification",
                                                "Session.track_browser_button_on", "Session.device_browser_button_on",
                                                "Session.track_faders_on", "Session.return_track_faders_on"]
                self._session_button_off_leds = ["Session.launch_q_button_off", "Session.record_q_button_off",
                                                 "Launchpad.off",
                                                 "Session.track_browser_button_off", "Session.device_browser_button_off",
                                                 "Session.track_faders_off", "Session.return_track_faders_off"]

                self._misc_button_row = 7

                self._session_button_priority = [-1]
                self._rec_utility_done = False
                
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._song.view.add_selected_track_listener(self.update_clip_selection)
                self._song.view.add_selected_track_listener(self._device_track_toggle)
                self._song.view.add_selected_chain_listener(self._device_track_toggle)
                self._song.view.add_selected_scene_listener(self.update_clip_selection)

                self._song.add_clip_trigger_quantization_listener(self._on_clip_trigger_quantization_changed_in_live)
                self._song.add_midi_recording_quantization_listener(self._on_record_quantization_changed_in_live)
                self._song.add_tracks_listener(self._count_tracks)
                
                self._song.set_data("creating_track", False)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                self._launch_q = self._song.clip_trigger_quantization
                self._selected_clip_slot_buffer = None

                self._record_q = self._song.midi_recording_quantization
                self._slot_copy_buffer = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                self._preset_list = Preset_List
                self._total_tracks = 0
                self._dummy_tracks = 0
                self._track_creation_in_progress = False
                self._insert_track_queue = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._preset_type = 0
                self._track_toggle = False #False = Track, True = Return_Track.
                self._device_position = False #False = Front, True = Back
                self._file_path = [0]
                self._browser_item = self.application().browser.user_library.children[self._file_path[0]]
                self._device_insert_action = time.time()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                self._volume_faders = []

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                self._count_tracks()
                self.update()

####################################################################################################################################

        def set_enabled(self, enabled):                                                         
                SessionComponent.set_enabled(self, enabled)
                if enabled:
                        for i in range(len(self._session_buttons)):
                                self._session_buttons[i] = self._side_buttons[i]
                                self._session_buttons[i].add_value_listener(self._session_button_value, identify_sender = True)
                                self._session_buttons[i].set_on_off_values(self._session_button_on_leds[i], self._session_button_off_leds[i])
                                self._session_buttons[i].turn_off()
                else:
                        for i in range(len(self._session_buttons)):
                                if self._session_buttons[i] != None:
                                        self._session_buttons[i].remove_value_listener(self._session_button_value)
                                        self._session_buttons[i] = None
                self._setup_matrix_buttons()

        def _setup_matrix_buttons(self):
                for y in range(self._num_scenes):
                        for x in range(self._num_tracks):
                                button = self._matrix.get_button(x, y)
                                button.set_on_off_values("Launchpad.off", "Launchpad.off")
                                button.suppress_script_forwarding = False
                                if self.is_enabled() and y < self._matrix.height():
                                        self.scene(y).clip_slot(x).set_triggered_to_play_value("Session.triggered")
                                        self.scene(y).clip_slot(x).set_triggered_to_record_value("Session.triggered")
                                        self.scene(y).clip_slot(x).set_stopped_value("Session.stopped")
                                        self.scene(y).clip_slot(x).set_recording_value("Session.recording")
                                        self.scene(y).clip_slot(x).set_started_value("Session.started")
                                        self.scene(y).clip_slot(x).set_launch_button(button)
                                        self.scene(y).clip_slot(x).set_parent(self)
                                        if self.scene(y).clip_slot(x)._clip_slot == self._song.view.highlighted_clip_slot:
                                                self._selected_clip_slot_buffer = self.scene(y).clip_slot(x)
                                else:
                                        self.scene(y).clip_slot(x).set_launch_button(None)

####################################################################################################################################

        def _session_button_value(self, value, sender):
                if self.is_enabled():
                        index = self._session_buttons.index(sender)
                        self._matrix_changed = index in (0, 1, 3, 4, 5, 6)
                        
                        if self._matrix_changed:
                                sender.toggle(index == self._session_button_priority[0])
                                if value != 0:
                                        self._session_button_priority.insert(-2, index)
                                else:
                                        self._session_button_priority.remove(index)
                                sender.toggle(index == self._session_button_priority[0])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                        elif index == 2:
                                for track in self._song.tracks:
                                        if track.can_be_armed and not track.current_monitoring_state == 0:
                                                track.arm = True
                                sender.turn_off()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                        if self._insert_track_queue != None and value == 0:
                                preset = self._preset_list[self._insert_track_queue]
                                util_track = self._song.create_midi_track(len(self._song.tracks))
                                util_track.name = preset.util['name']
                                util_track.color_index = preset.util['color'][self._insert_track_queue%len(preset.util['color'])]
                                util_track.current_monitoring_state = preset.util['current_monitoring_state']
                                #util_track.current_input_routing = preset.util['current_input_routing']
                                #util_track.current_input_sub_routing = preset.util['current_input_sub_routing']
                                #util_track.current_output_routing = self._song.return_tracks[-1].name
                                self._insert_track_queue = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                        self.update()

####################################################################################################################################

        def update_clip_selection(self):
                if self._selected_clip_slot_buffer != None:
                        self._selected_clip_slot_buffer.update()
                self._find_selected_clip_slot()
                self._slot_copy_buffer = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def update(self):
                SessionComponent.update(self)
                if self._matrix_changed:
                        self._update_matrix_leds(self._session_button_priority[0])
                        self._matrix_changed = False

        def _update_matrix_leds(self, mode):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# FADER AS LAUNCH CONTROL XL SCRIPT MONKEYPATCH #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                #self._control_surface.send_midi(SYSEX_HEADER + SYSEX_PARAMETERS['Default'] + SYSEX_END)
                #self._song.master_track.set_data('Monkey_Mode', False)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# FADER AS LAUNCH CONTROL XL SCRIPT MONKEYPATCH #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                if mode == -1:
                        for y in range(self._num_scenes):
                                for x in range(self._num_tracks):
                                        button = self._matrix.get_button(x, y)
                                        self._remove_all_listeners(button)
                                        button.set_on_off_values("Launchpad.off", "Launchpad.off")
                                        if x < len(self._song.tracks):
                                                self.scene(y).clip_slot(x).set_launch_button(button)
                                                self.scene(y).clip_slot(x).update()
                                        else:
                                                button.turn_off()
                                                
                        for fader in self._volume_faders:
                                fader.disconnect()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                if mode in (0, 1):
                        for x in range(8):
                                self.scene(self._misc_button_row).clip_slot(x).set_launch_button(None)
                                button = self._matrix.get_button(x, self._misc_button_row)
                                self._remove_all_listeners(button)
                                button.set_on_off_values(self._session_button_on_leds[mode], self._session_button_off_leds[mode])
                                button.add_value_listener((self._record_quantization_changed if mode else self._launch_quantization_changed), identify_sender = True)
                                button.toggle((Record_Q_Rates[x] == self._record_q) if mode else (Launch_Q_Rates[x] == self._launch_q))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                if mode in (3, 4):
                        if not self._rec_utility_done:
                                self._do_rec_utility()
                        for x in range(8):
                                for y in range(8):
                                        button = self._matrix.get_button(x, y)
                                        self._remove_all_listeners(button)
                                        button.set_on_off_values("Launchpad.off", "Launchpad.off")
                                        button.turn_off()
                                        self.scene(y).clip_slot(x).set_launch_button(None)

                                        if (mode == 3) and x < len(self._preset_list):
                                                if self._preset_list[x].unique and y > 0:         
                                                        continue
                                                if self._preset_list[x]._num_copies >= y:
                                                        self._make_create_track_button(button)

                                        if (mode == 4):
                                                if y == 0:
                                                        if x < Device_Preset_Types:
                                                                button.set_on_off_values("DeviceBrowser.folder_selected", "DeviceBrowser.folder")
                                                                button.add_value_listener(self._select_browser_item, identify_sender = True)
                                                                button.toggle(x == self._file_path[0] - 1)
                                                        elif Device_Preset_Types == x:
                                                                button.set_on_off_values("DeviceBrowser.return_type", "DeviceBrowser.track_type")
                                                                button.add_value_listener(self._device_track_toggle_button, identify_sender = True)
                                                                button.toggle(self._track_toggle)
                                                        else:
                                                                button.set_on_off_values("DeviceBrowser.position_back", "DeviceBrowser.position_front")
                                                                button.add_value_listener(self._toggle_device_position, identify_sender = True)
                                                                button.toggle(not self._device_position and x < 7)
                                                self._device_browser_update()
                                                self._device_track_toggle()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                if mode in (5, 6):
                        if not self._rec_utility_done:
                                self._do_rec_utility()
                        sliders = []
                        for x in range(8):
                                button_row = []
                                for y in range(7, -1, -1):
                                        button = self._matrix.get_button(x, y)
                                        self._remove_all_listeners(button)
                                        button.set_on_off_values("Launchpad.off", "Launchpad.off")
                                        button.turn_off()
                                        button_row.append(button)
                                sliders.append(tuple(button_row))
                        for i, track in enumerate(self._song.tracks if mode == 5 else self._song.return_tracks):
                                #Donkey_if
                                if not i > 7:
                                        volume_fader = ButtonSliderElement(tuple(sliders[i]))
                                        volume_fader.connect_to(track.mixer_device.volume)
                                        volume_fader.add_value_listener(self._volume_fader_led_update)
                                        self._volume_faders.append(volume_fader)
                                        
                        self._volume_fader_led_update(0)
                        

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~testing~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _volume_fader_led_update(self, value):
                self._song.master_track.set_data('Display_Faders', self._session_button_priority[0])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~testing~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                        

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
        def _remove_all_listeners(self, button):
                button.remove_value_listener(self._launch_quantization_changed)
                button.remove_value_listener(self._record_quantization_changed)
                button.remove_value_listener(self._create_track)
                button.remove_value_listener(self._select_browser_item)
                button.remove_value_listener(self._device_track_toggle_button)
                button.remove_value_listener(self._toggle_device_position)
                button.remove_value_listener(self._select_track)
                button.remove_value_listener(self._select_chain)
                button.device_index = None
                        

####################################################################################################################################

        def _launch_quantization_changed(self, value, sender):
                if self.is_enabled() and value != 0:
                        selected_q = Launch_Q_Rates[sender.x_index]
                        q_turned_off = self._launch_q == selected_q

                        if self._launch_q != Launch_Q.q_no_q:
                                self._matrix.get_button(Launch_Q_Rates.index(self._launch_q), self._misc_button_row).turn_off()
                        sender.toggle(not q_turned_off)

                        if q_turned_off:
                                self._song.clip_trigger_quantization = Launch_Q.q_no_q
                        else:
                                self._song.clip_trigger_quantization = selected_q
        
        def _on_clip_trigger_quantization_changed_in_live(self):
                self._launch_q = self._song.clip_trigger_quantization
                self._control_surface.show_message('Launch Quantization: %s' % Launch_Q_Names[int(self._launch_q)])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
           
        def _record_quantization_changed(self, value, sender):
                if self.is_enabled() and value != 0:
                        selected_q = Record_Q_Rates[sender.x_index]
                        q_turned_off = self._record_q == selected_q

                        if self._record_q != Record_Q.rec_q_no_q:
                                self._matrix.get_button(Record_Q_Rates.index(self._record_q), self._misc_button_row).turn_off()
                        sender.toggle(not q_turned_off)

                        if q_turned_off:
                                self._song.midi_recording_quantization = Record_Q.rec_q_no_q
                        else:
                                self._song.midi_recording_quantization = selected_q

        def _on_record_quantization_changed_in_live(self):
                self._record_q = self._song.midi_recording_quantization
                self._control_surface.show_message('Record Quantization: %s' % Record_Q_Names[int(self._record_q)])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _move_misc_button_row(self, index):
                self._misc_button_row += index if index else -1
                self._misc_button_row = self._misc_button_row % 8
                self._update_matrix_leds(-1)
                self._matrix_changed = True
                self.update()

####################################################################################################################################

        def _make_create_track_button(self, button):
                button.set_on_off_values("TrackBrowser.created", "TrackBrowser.available")
                button.add_value_listener(self._create_track, identify_sender = True)
                button.toggle(self._preset_list[button.x_index]._num_copies > button.y_index)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                  
        def _create_track(self, value, sender):
                if self.is_enabled():
                        preset = self._preset_list[sender.x_index] #Shorten the Track to be inserted
                        position = sender.y_index
                        for i in range(sender.x_index):
                                position += self._preset_list[i]._num_copies
                        now = time.time()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                        if preset._num_copies == sender.y_index and value != 0:
                                if sender.y_index >= preset._num_copies:
                                        self._track_creation_in_progress = True
                                        self._song.set_data("creating_track", True)
                                        if preset.ttype == "midi":
                                                track = self._song.create_midi_track(position)
                                                self.application().browser.load_item(self.application().browser.user_library.children[0].children[0])
                                        if preset.ttype == "audio":
                                                track = self._song.create_audio_track(position)
                                                track.current_monitoring_state = 1
                                        if preset.ttype == "returntrack":
                                                track = self._song.create_return_track()
                                                if preset.unique:
                                                        #self.application().browser.load_item(self.application().browser.user_library.children[0].children[preset.deviceid])
                                                        pass
                                        if hasattr(preset, "name"):
                                                track.name = preset.name if preset.unique else preset.name + (" %d" % (preset._num_copies + 1))
                                        if hasattr(preset, "color"):
                                                track.color_index = preset.color[sender.y_index%len(preset.color)]
                                        if hasattr(preset, "input_routing"):

                                                #If you don't succeed
                                                track.current_input_routing = preset.input_routing
                                                #Try and try again
                                                
                                        if hasattr(preset, "input_sub_routing"):

                                                #idea is to check for available control surfaces
                                                track.current_input_sub_routing = preset.input_sub_routing
                                                #and design track preset creation around that

                                        elif preset.ttype == "midi":
                                                track.current_input_sub_routing = "Ch. %s" % (preset._num_copies + 2)
                                        track.current_output_routing = "Sends Only"
                                        track.mixer_device.sends[0].value = 1.0
                                        if track.can_be_armed:
                                                track.arm = True
                                        if hasattr(preset, "util"):
                                                self._insert_track_queue = sender.x_index

                                sender.turn_on()
                                if not preset.unique:
                                        button = self._matrix.get_button(sender.x_index, sender.y_index + 1)
                                        self._make_create_track_button(button)

                        elif preset._num_copies == sender.y_index and value == 0:
                                self._song.set_data("creating_track", False)
                                self._count_tracks()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                        elif preset._num_copies > sender.y_index and value != 0:
                                self._last_action = now
                                
                        elif preset._num_copies > sender.y_index and value == 0:
                                if now - self._last_action > LONG_PRESS:
                                        self._song.set_data("creating_track", True)
                                        
                                        if preset.ttype != "returntrack":
                                                position = position - sender.y_index + preset._num_copies - 1
                                                self._song.delete_track(position)
                                        else:
                                                if hasattr(preset, 'util'): #Needs to choose the before-last return track IF there is a misc preset track ###
                                                        self._song.delete_return_track(len(self._song.return_tracks) - 1)
                                                        self._song.delete_track(len(self._song.tracks) - 1)
                                                else:
                                                        self._song.delete_return_track(len(self._song.return_tracks) - self._preset_list[-2]._num_copies - 1)
                                                        
                                        self._matrix.get_button(sender.x_index, preset._num_copies - 1).turn_off()
                                        if not preset.unique:
                                                button = self._matrix.get_button(sender.x_index, preset._num_copies)
                                                self._remove_all_listeners(button)
                                                button.set_on_off_values("Launchpad.off", "Launchpad.off")
                                                button.turn_off()                                                
                                                        
                                        self._song.set_data("creating_track", False)
                                        self._count_tracks()

####################################################################################################################################

        def _select_browser_item(self, value, sender):
                if self.is_enabled() and value != 0:
                        depth = sender.device_index[0] if sender.device_index != None else sender.y_index
                        index = sender.device_index[1] if sender.device_index != None else sender.x_index

                        if depth == 0: #Row 01: Reset Browser
                                self._file_path = [(index + 1)*int(index + 1 != self._file_path[0])]
                                self._browser_item = self.application().browser.user_library.children[self._file_path[0]]
                        elif depth + 1 == len(self._file_path) and self._file_path[depth] == index:
                                return #Prevents jumping around/misclicks
                        else:
                                for d in range(depth, len(self._file_path)):
                                        self._file_path.pop(-1)
                                self._file_path.append(index)
                                self._browser_item = self.application().browser.user_library.children[self._file_path[0]]
                                for i in range(1, len(self._file_path)):
                                        self._browser_item = self._browser_item.children[self._file_path[i]]
                        self._device_browser_update()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _device_track_toggle_button(self, value, sender):
                if self.is_enabled() and value != 0:
                        self._track_toggle = not self._track_toggle
                        sender.toggle(self._track_toggle)
                        self._device_track_toggle(True)

        def _device_track_toggle(self, via_toggle_button = False): #Name is not particularly unambiguous --- primary function is LED Management
                if self.is_enabled() and self._session_button_priority[0] == 4:
                        instrument_selector = None
                        chain_index = -1
                        track_index = [-1, -1]
                        if not via_toggle_button:
                                self._track_toggle = not self._song.view.selected_track in self._song.tracks

                        if self._song.view.selected_track in self._song.tracks:
                                for i in range(len(self._song.tracks)):
                                        if self._song.view.selected_track == self._song.tracks[i]:
                                                track_index[0] = i
                                if self._song.view.selected_track.can_show_chains:
                                        instrument_selector = self._song.view.selected_track.devices[0].chains[0]
                        if self._song.view.selected_chain != None and instrument_selector.devices[0] != None:
                                if self._song.view.selected_chain in instrument_selector.devices[0].chains:
                                        for i in range(len(instrument_selector.devices[0].chains)):
                                                if self._song.view.selected_chain == instrument_selector.devices[0].chains[i]:
                                                        chain_index = i
                        if self._song.view.selected_track in self._song.return_tracks:
                                for i in range(len(self._song.return_tracks)):
                                        if self._song.view.selected_track == self._song.return_tracks[i]:
                                                track_index[1] = i - (2*int(self._rec_utility_done))
                
                        for c in range(16):
                                button = self._matrix.get_button(c % 8, 5 + int(c/8))
                                self._remove_all_listeners(button)
                                button.set_on_off_values("Launchpad.off", "Launchpad.off")
                                button.turn_off()
                        for t in range(8):
                                button = self._matrix.get_button(t, 7)
                                button.clear_send_cache()
                                button.states[True] = "DeviceBrowser.return_type" if t < len(self._song.return_tracks)-(2*int(self._rec_utility_done)) else "Launchpad.off"
                                button.states[False] = "DeviceBrowser.track_type" if t < len(self._song.tracks) else "Launchpad.off"
                                button.add_value_listener(self._select_track, identify_sender = True)
                                button.toggle(self._track_toggle)
                        if 8 > track_index[int(self._track_toggle)] >= 0:
                                self._matrix.get_button(track_index[int(self._track_toggle)], 7).set_light("DeviceBrowser.track_selected")
                                if not self._track_toggle and instrument_selector != None:
                                        try:
                                                for c in range(len(instrument_selector.devices[0].chains)):
                                                        button = self._matrix.get_button(c % 8, 5 + int(c/8))
                                                        button.set_on_off_values("DeviceBrowser.chain_selected", "DeviceBrowser.chain")
                                                        button.add_value_listener(self._select_chain, identify_sender = True)
                                                        button.toggle(c == chain_index)
                                        except IndexError:
                                                self._control_surface.log_message("Instrument Selector Cannot Show Chains")
                        if not self.application().view.is_view_visible('Detail/DeviceChain'):
                                self.application().view.show_view('Detail/DeviceChain')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                                
        def _toggle_device_position(self, value, sender):
                if self.is_enabled() and value != 0:
                        self._device_position = sender.x_index == 7
                        self._matrix.get_button(6, 0).toggle(not self._device_position)
                        self._matrix.get_button(7, 0).toggle(self._device_position)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Select Track/Chain Long presses to insert a device are not index-specific (e.g. press Button 1 -> press Button 7 -> wait 0.5sec -> release button 1, then button 7 -> insert device in track 7 twice)

        def _select_chain(self, value, sender):
                if self.is_enabled():
                        t = time.time()
                        if value != 0:
                                self._device_insert_action = t
                                index = (sender.x_index) + ((sender.y_index - 5)*8)
                                self._song.view.selected_chain = self._song.view.selected_track.devices[0].chains[0].devices[0].chains[index]
                        else:
                                if t - self._device_insert_action > LONG_PRESS:
                                        self._insert_device()

        def _select_track(self, value, sender):
                if self.is_enabled():
                        t = time.time()
                        if value != 0:
                                self._device_insert_action = t
                                if self._track_toggle:
                                        self._song.view.selected_track = self._song.return_tracks[sender.x_index + 2*int(self._rec_utility_done)]
                                else:
                                        self._song.view.selected_track = self._song.tracks[sender.x_index]
                        else:
                                if t - self._device_insert_action > LONG_PRESS:
                                        self._insert_device()

        def _insert_device(self):
                if self.is_enabled() and not self._browser_item.is_folder:
                        
                        DeviceInsertMode = Live.Track.DeviceInsertMode
                        
                        if self._file_path[0] == 5:
                                if self._device_position:
                                        self.song().view.selected_track.view.device_insert_mode = DeviceInsertMode.selected_right
                                else:
                                        self.song().view.selected_track.view.device_insert_mode = DeviceInsertMode.selected_left
                        else:
                                self.song().view.selected_track.view.device_insert_mode = DeviceInsertMode.default

                        if self._browser_item.is_loadable:
                                self.application().browser.load_item(self._browser_item)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                                
        def _device_browser_update(self):
                if self.is_enabled() and self._session_button_priority[0] == 4:
                        item = self.application().browser.user_library
                        sub_index = 0

                        for dtype in range(5):
                                self._matrix.get_button(dtype, 0).toggle(self._file_path[0] == dtype + 1)

                        for i in range(32):
                                button = self._matrix.get_button(i % 8, 1 + int(i/8))
                                button.set_on_off_values("Launchpad.off", "Launchpad.off")
                                self._remove_all_listeners(button)
                                button.turn_off()

                        for i in range(len(self._file_path)):
                                if item.is_folder:
                                        item = item.children[self._file_path[i]]
                                        for x in range(len(item.children)):
                                                button = self._matrix.get_button(x % 8, 1 + i + sub_index + int(x/8))
                                                button.add_value_listener(self._select_browser_item, identify_sender = True)
                                                button.device_index = [i + 1, x]
                                                if item.children[x].is_folder:
                                                        button.set_on_off_values("DeviceBrowser.folder_selected", "DeviceBrowser.folder")
                                                else:
                                                        button.set_on_off_values("DeviceBrowser.item_selected", "DeviceBrowser.item")
                                                if i + 1 < len(self._file_path):
                                                        button.toggle(x == self._file_path[i+1])
                                                else:
                                                        button.turn_off()
                                        sub_index += int((len(item.children)-1)/8)
                                if sub_index > MAX_DEVICE_SELECTION_ROWS:
                                        break

####################################################################################################################################
  
        def _do_rec_utility(self):
                utility_setup_a = False
                utility_setup_b = False

                if len(self._song.return_tracks) > 1:
                        if "A-REC" in self._song.return_tracks[0].name:
                                utility_setup_a = True
                        if "B-REC" in self._song.return_tracks[1].name:
                                utility_setup_b = True
                        if utility_setup_a and utility_setup_b:
                                self._song.return_tracks[0].current_output_routing = "Master"
                                self._song.return_tracks[1].current_output_routing = "Sends Only"
                                self._rec_utility_done = True
                                
                if not self._rec_utility_done:
                        for track in self._song.return_tracks:
                                self._song.delete_return_track(0)

                        self._song.create_return_track()
                        self._song.create_return_track()
                        self._song.return_tracks[0].name = "REC"
                        self._song.return_tracks[0].color_index = 14
                        self._song.return_tracks[0].current_output_routing = "Sends Only"
                        self._song.return_tracks[1].name = "REC"
                        self._song.return_tracks[1].color_index = 14
                        self._song.return_tracks[1].current_output_routing = "Master"
                        self._control_surface.log_message(str(self._song.return_tracks[0].output_routing_type))# = "Sends Only"
                        self._rec_utility_done = True

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _find_selected_clip_slot(self):
                track = self._song.view.selected_track
                self._track_toggle = (track in self._song.return_tracks) and ("REC" not in track.name)

                for x, track in enumerate(self._song.tracks):
                        for y in range(len(self._song.scenes)):
                                try:
                                        if self.scene(y).clip_slot(x)._clip_slot == self._song.view.highlighted_clip_slot:
                                                self._selected_clip_slot_buffer = self.scene(y).clip_slot(x)
                                                self._selected_clip_slot_buffer.update()
                                except IndexError:
                                        continue

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _count_tracks(self):
                if self.is_enabled() and not self._song.get_data("creating_track", True):
                        arm_state = False
                        
                        for track in self._song.tracks:
                                if track.can_be_armed and not track.current_monitoring_state == 0:
                                        if not track.arm_has_listener(self._count_tracks):
                                                track.add_arm_listener(self._count_tracks)
                                                self._total_tracks = 0
                                        if not track.arm:
                                                arm_state = True

                        if self._session_buttons[2] != None:
                                self._session_buttons[2].toggle(arm_state)

                        dummy = len(self._song.tracks) + len(self._song.return_tracks) - 2*int(self._rec_utility_done)
                        if self._total_tracks + self._dummy_tracks != dummy:
                                self._recount_tracks(dummy)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _recount_tracks(self, dummy):
                self._total_tracks = 0
                self._dummy_tracks = 0
                mpb = 0                 #Missing Preset Buffer
                mpbr = -1               #Missing Preset Buffer (Returns)

                for index, preset in enumerate(self._preset_list):
                        preset._num_copies = 0
                        try:
                                if hasattr(preset, "name"):
                                        if preset.unique:
                                                copy = 1
                                        else:
                                                copy = self._preset_depth(preset, index-mpb) 
                                        if (preset.name in self._song.tracks[index-mpb].name) or (preset.name in self._song.return_tracks[mpbr].name):
                                                preset._num_copies += copy #Bug waiting to happen: Return Presets with the same name as Instrument Presets
                                                self._total_tracks += copy
                                                mpb += (1 - copy) * int(preset.ttype != "returntrack")
                                                mpbr -= 1 * int(preset.ttype == "returntrack")
                                        else:
                                                mpb += 1
                                else:   #This should only apply to nameless non-unique return tracks
                                        copy = self._preset_depth(preset, mpbr, True) #Counting Return Tracks from back to front
                                        preset._num_copies += copy
                                        self._total_tracks += copy
                                        mpbr -= copy
                        except IndexError:
                                mpb += 1

                for remaining_track in range(dummy):
                        self._dummy_tracks += 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _preset_depth(self, preset, index, returntrack = False):
                if returntrack:
                        for depth in range(len(self._song.return_tracks)):
                                if "REC" not in self._song.return_tracks[index-depth].name:
                                        continue
                                else:
                                        return depth
                else:
                        depth_index = 0
                        for depth in range(index, len(self._song.tracks)):
                                if preset.name in self._song.tracks[depth].name:
                                        depth_index += 1
                                else:
                                        break
                        return depth_index
                return 0

####################################################################################################################################

        def link_with_track_offset(self, track_offset):
                assert (track_offset >=0)
                if self._is_linked():
                        self._unlink()
                self.set_offsets(track_offset, 0)
                self._link()

        def unlink(self):
                if self._is_linked():
                        self._unlink()

        def _reassign_tracks(self):
                SessionComponent._reassign_tracks(self)

