import Live

class DrumTrack:
    unique = True
    name = "Drums"
    color = [2]
    input_routing = "MPD218RS Input (MPD218V)"
    input_sub_routing = "Ch. 1"
    ttype = "midi"

class BassTrack:
    unique = True
    name = "Bass"
    color = [23]
    input_routing = "MPKMiniRS Input (MPKMiniV)"
    input_sub_routing = "Ch. 1"
    ttype = "midi"

class SeaboardTrack:
    unique = True
    name = "Seaboard"
    color = [24]
    input_routing = "Seaboard RISE 49"
    input_sub_routing = "All Channels"
    ttype = "midi"

class KeyboardTrack:
    unique = False
    name = "Keyboard"
    color = [47]
    input_routing = "H89RS Input (H89Controls)"
    ttype = "midi"

class LaneTrack:
    unique = False
    name = "LANE"
    color = [25]
    input_routing = "B-REC"
    ttype = "audio"

class FXSequencerReturnTrack:
    unique = True
    name = "FX Sequencer"
    color = [58]
    util = {"name"                      :   "FXMIDI",
            "color"                     :   color,
            "current_input_routing"     :   "LPMiniRS Input (LPMini)",
            "current_input_sub_routing" :   "Ch. 4",
            "current_monitoring_state"  :   0,
            "current_output_routing"    :   name}
    deviceid = 3
    ttype = "returntrack"

class DefaultReturnTrack:
    unique = False
    color = [3]
    ttype = "returntrack"

Preset_List = [
    DrumTrack,
    BassTrack,
    SeaboardTrack,
    KeyboardTrack,
    LaneTrack,
    FXSequencerReturnTrack,
    DefaultReturnTrack]

####################################################################################################################################
Launch_Q = Live.Song.Quantization
Launch_Q_Rates = [
    Launch_Q.q_8_bars,
    Launch_Q.q_4_bars,
    Launch_Q.q_2_bars,
    Launch_Q.q_bar,
    Launch_Q.q_half,
    Launch_Q.q_quarter,
    Launch_Q.q_eight,
    Launch_Q.q_sixtenth,]
Launch_Q_Names = ('None', '8 Bars', '4 Bars', '2 Bars', '1 Bar', '1/2','Dummy', '1/4', 'Dummy', '1/8','Dummy', '1/16')

Record_Q = Live.Song.RecordingQuantization
Record_Q_Rates = [
    Record_Q.rec_q_quarter,
    Record_Q.rec_q_eight,
    Record_Q.rec_q_eight_triplet,
    Record_Q.rec_q_eight_eight_triplet,
    Record_Q.rec_q_sixtenth,
    Record_Q.rec_q_sixtenth_triplet,
    Record_Q.rec_q_sixtenth_sixtenth_triplet,
    Record_Q.rec_q_thirtysecond]
Record_Q_Names = ('1/4', '1/8', '1/8t', '1/8+t', '1/16', '1/16t', '1/16+t', '1/32')

Device_Preset_Types = 5
MAX_DEVICE_SELECTION_ROWS = 4



        
