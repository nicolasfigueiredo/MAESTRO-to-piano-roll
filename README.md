# MAESTRO-to-piano-roll

A Python function that converts MIDI files from the MAESTRO dataset into a Numpy 2D array representing the performance's piano roll, by processing note-on/off events along with the piano sustain pedal control messages. MIDI files from the MAESTRO dataset have the following characteristics:

- Note off events are captured as note on events with zero velocity;
- Several messages are sent during one pressing motion of the sustain pedal;
- All relevant messages are in track 1 of the MIDI file

Dependencies: numpy and Mido.
To do: simple decay model