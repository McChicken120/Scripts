from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement

####################################################################################################################################

class SamplerComponent(CompoundComponent):

        def __init__(self, matrix, side_buttons, control_surface):
                super(SamplerComponent, self).__init__()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
                self._control_surface = control_surface

                self._matrix = matrix
                
                self._side_buttons = side_buttons
                self._sampler_buttons = [None, None, None, None, None, None, None]
                self._sampler_button_on_leds = ["EmptyButton", "EmptyButton", "EmptyButton",
                                                "EmptyButton", "EmptyButton", "EmptyButton",
                                                "EmptyButton"]
                self._sampler_button_off_leds = ["EmptyButton", "EmptyButton", "EmptyButton",
                                                 "EmptyButton", "EmptyButton", "EmptyButton",
                                                 "EmptyButton"]

####################################################################################################################################

        def set_enabled(self, enabled):
                if enabled:
                        note = 36
                        
                        for y in range(7, -1 , -1):
                                for x in range(8):
                                        button = self._matrix.get_button(x, y)
                                        button.set_identifier(note)
                                        button.set_channel(3)
                                        button.set_light("Sampler.default")
                                        button.suppress_script_forwarding = True

                                        note += 1

                        for i in range(len(self._sampler_buttons)):
                                self._sampler_buttons[i] = self._side_buttons[i]
                                self._sampler_buttons[i].add_value_listener(self._sampler_button_value, identify_sender = True)
                                self._sampler_buttons[i].set_on_off_values(self._sampler_button_on_leds[i], self._sampler_button_off_leds[i])

                        self._update_buttons()
                else:
                        for x in range(8):
                                for y in range(8):
                                        self._matrix.get_button(x, y).suppress_script_forwarding = False

                        for i in range(len(self._sampler_buttons)):
                                if self._sampler_buttons[i] != None:
                                        self._sampler_buttons[i].remove_value_listener(self._sampler_button_value)
                                        self._sampler_buttons[i] = None

                CompoundComponent.set_enabled(self, enabled)

        def _update_buttons(self):
                if self.is_enabled():
                        for button in self._sampler_buttons:
                                button.turn_off()

####################################################################################################################################

        def _sampler_button_value(self, value, sender):
                if self.is_enabled():
                        pass

        

                
        
