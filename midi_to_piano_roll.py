import mido
import numpy as np

def midi_to_piano_roll_new(midi_file, decay=False, decay_rate=28):
    # decay determines if a linear velocity decay rate will be applied to all notes (TO DO)
    # decay_rate is given in velocity per second


    # From a midi file, build a 2D array representing the piano roll
    decay_per_tick = decay_rate / mido.second2tick(1, tempo=500000, ticks_per_beat=midi_file.ticks_per_beat)
    ticks_in_track = np.ceil(mido.second2tick(midi_file.length, tempo=500000, ticks_per_beat=midi_file.ticks_per_beat))
    piano_roll = np.zeros([127, int(ticks_in_track)])   # piano roll with x axis labeled by ticks and y axis labeled by midi note number

    time = 0
    pedal_flag = False           # True if sustain pedal is pressed, 0 otherwise
    noteon_vel = np.zeros(127)   # velocity of pressed keys
    noteon_time = np.zeros(127, dtype='int') # time key was pressed
    keyrelease_flags = []

    for msg in midi_file.tracks[1]:
        time += msg.time
        if msg.type == 'note_on':
            if msg.velocity > 0:
                noteon_vel[msg.note] = msg.velocity
                noteon_time[msg.note] = time
            else: # note-off (note-offs are given as note-on events with velocity==0)
                if pedal_flag: # key was released, but sustain pedal keeps it sounding
                    keyrelease_flags.append(msg.note) # notes contained here will cease when sustain pedal is released
                else:
                    piano_roll[msg.note, noteon_time[msg.note]:time] = noteon_vel[msg.note]
        elif msg.type == 'control_change':
            if not pedal_flag and msg.value>0: # pedal sends several messages during one pressing motion
                pedal_flag = True
            elif pedal_flag and msg.value == 0:
                pedal_flag = False
                for note in keyrelease_flags: # these notes stopped playing
                    piano_roll[note, noteon_time[note]:time] = noteon_vel[note]
                    keyrelease_flags = []
                
    return piano_roll

def include_harmonics(piano_roll, n_harmonics=7, decay=False, decay_rate=7.86):
    # Takes a piano roll and augments it with n_harmonics for each note, with a simple decay model
    new_piano_roll = np.zeros([piano_roll.shape[0]+n_harmonics*12, piano_roll.shape[1]])    
    for i in range(127):
        new_piano_roll[i] = np.max([new_piano_roll[i], piano_roll[i]], axis=0) # overtones can fall on top of lines already containing notes
        for j in range(1,n_harmonics+1):
            if decay:
                partial = piano_roll[i] - decay_rate * j  # velocity atenuation per harmonic
            else:
                partial = piano_roll[i]
            new_piano_roll[i+12*j] = np.max([new_piano_roll[i+12*j], partial], axis=0)            
    return np.where(new_piano_roll >= 0, new_piano_roll, 0)