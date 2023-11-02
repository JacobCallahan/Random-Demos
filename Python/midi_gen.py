from os import popen
import random
from midiutil.MidiFile import MIDIFile
# from pydub.playback import play

# Define the number of tracks and tempo of the MIDI file
NUM_TRACKS = 4
TEMPO = 120

# Define the available instruments
INSTRUMENTS = {
    0: 'Acoustic Grand Piano',
    24: 'Nylon Guitar',
    32: 'Acoustic Bass',
    40: 'Violin'
}

# Define the available chords and chord progressions
CHORDS = {
    'C': [0, 4, 7],
    'C#m': [1, 5, 8],
    'D': [2, 6, 9],
    'E': [4, 8, 11],
    'Em': [4, 7, 11],
    'F': [5, 9, 0],
    'G': [7, 11, 2],
    'A': [9, 1, 4],
    'Am': [9, 0, 4],
    'B': [11, 3, 6],
    'Bm': [11, 2, 6],
}
CHORD_PROGRESSIONS = [
    ['C', 'G', 'Am', 'F'],
    ['G', 'D', 'Em', 'C'],
    ['D', 'A', 'Bm', 'G'],
    ['E', 'B', 'C#m', 'A']
]

# Define the time signature (e.g., 4/4, 3/4, etc.)
TIME_SIGNATURE = (4, 4)

# Define the number of measures and duration of each measure
NUM_MEASURES = 16
MEASURE_DURATION = 4.0

# Define the MIDIFile object with the specified parameters
midi = MIDIFile(NUM_TRACKS)
midi.addTempo(0, 0, TEMPO)

# Loop over each track and add notes
for i in range(NUM_TRACKS):
    # Set the instrument for this track
    instrument = random.choice(list(INSTRUMENTS.keys()))
    midi.addProgramChange(i, 0, 0, instrument)

    # Loop over each measure and add notes
    for j in range(NUM_MEASURES):
        # Choose a random chord progression for this measure
        chord_progression = random.choice(CHORD_PROGRESSIONS)

        # Loop over each beat in the measure and add notes
        for k in range(TIME_SIGNATURE[0]):
            # Choose a random chord for this beat
            chord = random.choice(chord_progression)

            # Loop over each note in the chord and add a MIDI note
            for note in CHORDS[chord]:
                # Choose a random velocity (volume) for the note
                velocity = random.randint(64, 127)

                # Calculate the start time and duration of the note
                start_time = (j * MEASURE_DURATION) + (k * (MEASURE_DURATION / TIME_SIGNATURE[0]))
                duration = MEASURE_DURATION / TIME_SIGNATURE[0]

                # modify the octave pitch of the note
                note = note + 12 * random.randint(0, 3)

                # Add the note to the MIDI file
                print(f"Adding note: {i, 0, note + (12 * (k//len(CHORDS[chord]))), start_time, duration, velocity}")
                midi.addNote(i, 0, note + (12 * (k//len(CHORDS[chord]))), start_time, duration, velocity)

# Write the MIDI file to disk
with open('random_music.mid', 'wb') as file:
    midi.writeFile(file)

# Convert the MIDI file to a WAV file using fluidsynth cli
popen('fluidsynth -F random_music.wav random_music.mid')
