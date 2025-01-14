from _Framework.CompoundComponent import CompoundComponent
from _Framework.ButtonElement import ButtonElement

import Live

####################################################################################################################################

class SongTempoComponent(CompoundComponent):

    def __init__(self, matrix, side_buttons, control_surface):
        super(SongTempoComponent, self).__init__()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        self._control_surface = control_surface

        self._matrix = matrix
        self._side_buttons = side_buttons

        self._tempo_buttons = [None, None, None, None, None, None, None]
        self._tempo_button_on_leds = ["Launchpad.off", "Launchpad.off", "Launchpad.off",
                                      "Launchpad.off", "Launchpad.off", "Launchpad.off", "Launchpad.off"]
        self._tempo_button_off_leds = ["Launchpad.off", "Launchpad.off", "Launchpad.off",
                                       "Launchpad.off", "Launchpad.off", "Launchpad.off", "Launchpad.off"]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        self.song().add_current_song_time_listener(self._song_time_value)
        self._tempo = None #self.song().tempo

####################################################################################################################################

    def set_enabled(self, enabled):
            self._build_tempo_button_matrix(enabled)
            self.update()

    def _build_tempo_button_matrix(self, enabled):
        for x in range(8):
            for y in range(8):
                button = self._matrix.get_button(x, y)
                if enabled:
                    button.x_index = x
                    button.y_index = y
                    button.add_value_listener(self._matrix_button_value, identify_sender = True)
                    on, off = self._get_button_colors(button)
                    button.set_on_off_values(on, off)
                    button.turn_off()
                else:
                    button.remove_value_listener(self._matrix_button_value)

####################################################################################################################################

    def update(self):
        if self.is_enabled():
            self._update_buttons()
            self._update_tempo()
    
    def _update_buttons(self):
        if self.is_enabled():
            pass

    def _update_tempo(self):
        if self.is_enabled():
            self._tempo = self.song().tempo

####################################################################################################################################

    def _song_time_value(self):
        pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    def _matrix_button_value(self, value, sender):
        if self.is_enabled() and value != 0:
            sender.turn_on()
            if sender.x_index > sender.y_index:
                self.song().tempo += (self.song().tempo)*(self._get_tempo_fraction(min(sender.x_index, sender.y_index), max(sender.x_index, sender.y_index)))
            elif sender.x_index < sender.y_index:
                self.song().tempo -= (self.song().tempo)*(self._get_tempo_fraction(min(sender.x_index, sender.y_index), max(sender.x_index, sender.y_index)))
            self.update_tempo()

        elif self.is_enabled():
            sender.turn_off()

    def _get_tempo_fraction(self, numerator, denominator):
        return (numerator+1)/(denominator+1)

    def _get_button_colors(self, button):
        x = button.x_index
        y = button.y_index
        if x == y:
            return 'Songtempo.diagonal_on', 'Songtempo.diagonal_off'
        else:
            On = 'Songtempo.button_pressed'
            tempo_fraction = self._get_tempo_fraction(min(x, y), max(x, y))
            if tempo_fraction > 0.5:
                return On, 'Songtempo.above_halftime'
            if tempo_fraction == 0.5:
                return On, 'Songtempo.halftime'
            if 0.5 > tempo_fraction > 0.25:
                return On, 'Songtempo.above_quartertime'
            if tempo_fraction == 0.25:
                return On, 'Songtempo.quartertime'
            if tempo_fraction < 0.25:
                return On, 'Songtempo.below_quartertime'       
        return 'Launchpad.off', 'Launchpad.off'


            
