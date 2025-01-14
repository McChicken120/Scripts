from _Framework.ButtonElement import ButtonElement, ON_VALUE, OFF_VALUE
from _Framework.Skin import SkinColorMissingError

####################################################################################################################################

class ConfigurableButtonElement(ButtonElement):

        default_states = {True: 'Launchpad.off', False: 'Launchpad.off'}
        send_depends_on_forwarding = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def __init__(self, is_momentary, msg_type, channel, identifier, skin = None, default_states = None, *a, **k):
                super(ConfigurableButtonElement, self).__init__(is_momentary, msg_type, channel, identifier, skin = skin, **k)
                
                if default_states is not None:
                        self.default_states = default_states
                        
                self.states = dict(self.default_states)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        @property
        def _on_value(self):
                return self.states[True]

        @property
        def _off_value(self):
                return self.states[False]

        @property
        def on_value(self):
                return self._try_fetch_skin_value(self._on_value)

        @property
        def off_value(self):
                return self._try_fetch_skin_value(self._off_value)

        def _try_fetch_skin_value(self, value):
                try:
                        return self._skin[value]
                except SkinColorMissingError:
                        return value

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def set_on_off_values(self, on_value, off_value = None):
                self.clear_send_cache()
                if off_value == None:
                        self.states[True] = str(on_value)+".On"
                        self.states[False] = str(on_value)+".Off"
                else:
                        self.states[True] = on_value
                        self.states[False] = off_value

        def toggle(self, condition):
                if condition:
                        self.turn_on()
                else:
                        self.turn_off()

        def set_light(self, value):
                try:
                        self._draw_skin(value)
                except SkinColorMissingError:
                        super(ButtonElement, self).set_light(value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
        def reset(self):
                self.set_light('Launchpad.off')
                self.reset_state()

        def reset_state(self):
                self.states = dict(self.default_states)
                super(ConfigurableButtonElement, self).reset_state()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def force_next_send(self):
                self._force_next_send = True
                self.clear_send_cache()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                
        def send_value(self, value, **k):
                if value is ON_VALUE:
                        self._do_send_on_value(**k)
                elif value is OFF_VALUE:
                        self._do_send_off_value(**k)
                elif type(value) is int:
                        super(ConfigurableButtonElement, self).send_value(value, **k)
                else:
                        self._draw_skin(value)
                        
        def _do_send_on_value(self, **k):
                if type(self._on_value) is int:
                        super(ConfigurableButtonElement, self).send_value(self._on_value, **k)
                else:
                        self._draw_skin(self._on_value)
                        
        def _do_send_off_value(self, **k):
                if type(self._off_value) is int:
                        super(ConfigurableButtonElement, self).send_value(self._off_value, **k)
                else:
                        self._draw_skin(self._off_value)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        def _draw_skin(self, value):
                self._skin[value].draw(self)



                        


