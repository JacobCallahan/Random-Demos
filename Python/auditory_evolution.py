"""
This is a script that uses genetic algortihms to generate midi music.
The user then votes on the top 3 of 10 randomly generated songs.
The top 3 songs are then used to generate the next generation of songs.
"""
import os
from pprint import pprint
import random
import string
import subprocess
import time
from collections import deque
import click
from midiutil.MidiFile import MIDIFile

MIDI_INPUTS = {
    "instruments": [0, 26, 33, 118, 48],
    "timing": {
        "tempo": [40, 60, 80, 100, 120, 140, 160, 180, 200],
        "time_signature": [("2/4", 24), ("3/4", 36), ("4/4", 48), ("6/8", 72)],
    },
    "controllers": ["volume", "modulation", "expression"],
    "chord_progressions": {
        "major": [
            ["C", "E", "G"],
            ["D", "F#", "A"],
            ["E", "G#", "B"],
            ["F", "A", "C"],
            ["G", "B", "D"],
            ["A", "C#", "E"],
            ["B", "D#", "F#"],
        ],
        "minor": [
            ["C", "D#", "G"],
            ["D", "F", "A"],
            ["E", "G", "B"],
            ["F", "G#", "C"],
            ["G", "A#", "D"],
            ["A", "C", "E"],
            ["B", "D", "F#"],
        ],
    },
    "effects": ["reverb", "delay", "chorus"],
}


class Population:
    """This class is the controller for the population of Orgamisms."""

    def __init__(
        self,
        population_count=20,
        population=None,
        top_scores=None,
        rev_pop_sort=False,
        generator_function=False,
        mutate=True,
    ):
        self.population_count = population_count
        self.population = population or []
        self.top_scores = top_scores or deque(maxlen=200)
        self.rev_pop_sort = rev_pop_sort
        self.generator_function = generator_function
        self.mutate = mutate
        self._generate_population()

    def _generate_population(self):
        """Generate a population of organisms."""
        self.population = []
        for _ in range(self.population_count):
            org = Organism(gen_func=self.generator_function)
            self.population.append(org)

    def _breed_pair(self, gene_list1, gene_list2):
        """Breed two gene lists together.

        The first has a greater chance of passing their genes on.
        Random mutation is then given a chance to change the child.

        """
        new_gene_list = []
        if gene_list1 and gene_list2:
            # If we have nested genes, then recursively breed them
            if isinstance(gene_list1[0], list):
                for list1, list2 in zip(gene_list1, gene_list2):
                    new_gene_list.append(self._breed_pair(list1, list2))
            else:
                crossover = random.randint(0, len(gene_list1))
                new_gene_list = gene_list1[:crossover]
                new_gene_list.extend(gene_list2[crossover:])
        else:
            new_gene_list = gene_list1
        return new_gene_list

    def breed_population(self, pool_percentage=50):
        """ "Cross breed the population with only the top percentage.

        :param pool_percentage: Percentage defines primary breeder cutoff.

        """
        # Create the breeding order. Those on top get more iterations.
        self.sort_population()
        breeders = self.population[
            : int(self.population_count * (float(pool_percentage) / 100))
        ]
        self.top_scores.append(breeders[0].points)
        # Add in some random members of the population
        while self.population_count > len(breeders):
            breeders.append(random.choice(self.population))

        next_generation = [
            Organism(genes=breeders[0].genes[:], gen_func=self.generator_function)
        ]  # keep our best
        # Randomly mutate our existing population
        if self.mutate:
            if (
                len(self.top_scores) == 200
                and self.top_scores[0] == self.top_scores[-1]
            ):
                mutation_chance = 0.9
            else:
                mutation_chance = 0.3
            for org in breeders:
                if random.random() <= mutation_chance:
                    org.mutate()

        while len(next_generation) < self.population_count:
            org1 = random.choice(breeders)
            org2 = random.choice(breeders)
            if org1 != org2:
                new_org = Organism(
                    genes=self._breed_pair(org1.genes, org2.genes),
                    gen_func=self.generator_function,
                )
            else:  # Avoid potential stagnation by introducing a new organism
                new_org = Organism(gen_func=self.generator_function)
            next_generation.append(new_org)
        self.population = next_generation

    def sort_population(self, reverse=None):
        """Sort the population by the number of points they have."""
        reverse = reverse or self.rev_pop_sort
        self.population = sorted(
            self.population, key=lambda org: org.points, reverse=reverse
        )


class Organism:
    def __init__(self, genes=None, gen_func=None, points=0):
        self.gen_func = gen_func
        if not genes:
            self.generate_genes()
        else:
            self.genes = genes
        self.points = points

    def generate_genes(self):
        """Randomly sort the genes to provide different combinations."""
        self.genes = self.gen_func()

    def mutate(self, mutation_chance=0.1):
        """Randomly mutate the genes, if dice rolls pass"""
        new_genes = self.gen_func()
        for i, _ in enumerate(self.genes):
            if random.random() <= mutation_chance:
                self.genes[i] = new_genes[i]

    def generate_song(self, t_id=None, duration=300):
        """Generate a song from the genes."""
        song = MidiTrack(
            effect=self.genes[0],
            num_notes=self.genes[1],
            pitch_range=self.genes[2],
            pitch_variability=self.genes[3],
            duration_range=self.genes[4],
            duration_variability=self.genes[5],
            velicity_range=self.genes[6],
            velocity_variability=self.genes[7],
        )
        song.generate_midi_file(duration=duration)
        try:
            return song.save_wav_file(t_id=t_id)
        except Exception as e:
            click.secho(f"Error saving wav file: {e}", fg="red")
            return f"{t_id}.mid"


class MidiTrack:
    def __init__(
        self,
        effect,
        num_notes,
        pitch_range,
        pitch_variability,
        duration_range,
        duration_variability,
        velicity_range,
        velocity_variability,
    ):
        self.effect = effect
        self.num_notes = num_notes
        self.pitch_range = pitch_range
        self.duration_range = duration_range
        self.pitch_variability = pitch_variability
        self.duration_variability = duration_variability
        self.velocity_range = velicity_range
        self.velocity_variability = velocity_variability
        self.notes = []

    def generate_notes(self, track_id, duration=300):
        """Generate a series of notes that equates to a duration equaling 30 seconds total"""
        _cur_note = random.randint(0, 128)
        _cur_duration = 4
        _cur_velocity = 75
        _total_duration = 0
        self.notes.append([])
        click.echo(f"Generating track {track_id}")
        while _total_duration < duration:
            # roll the dice to determine if we change the pitch
            if random.random() < self.pitch_variability:
                # if so, choice a note within range of the current note based on pitch_range
                _cur_note = random.randint(
                    _cur_note - self.pitch_range, _cur_note + self.pitch_range
                )
                # ensure the note is between 0 and 128
                if _cur_note < 0:
                    _cur_note = 0
                elif _cur_note > 128:
                    _cur_note = 128
            # roll the dice to determine if we change the duration
            if random.random() < self.duration_variability:
                # if so choose a duration that is within range of the current duration based on duration_range
                _cur_duration = random.randint(
                    _cur_duration - self.duration_range,
                    _cur_duration + self.duration_range
                )
                # ensure the note duration is at least 1
                if _cur_duration < 1:
                    _cur_duration = 1
            # roll the dice to determine if we change the velocity
            if random.random() < self.velocity_variability:
                # if so choose a velocity that is within range of the current velocity based on velocity_range
                _cur_velocity = random.randrange(
                    _cur_velocity - self.velocity_range,
                    _cur_velocity + self.velocity_range,
                )
                # ensure the velocity is between 64 and 127
                if _cur_velocity < 64:
                    _cur_velocity = 64
                elif _cur_velocity > 127:
                    _cur_velocity = 127
            # add the note to the notes list
            self.notes[track_id].append([_cur_note, _cur_duration, _cur_velocity])
            _total_duration += _cur_duration

    def generate_midi_file(self, duration=300):
        """Generate a midi file"""
        click.echo(f"Organism: {self}")
        [self.generate_notes(track_id, duration) for track_id in range(len(MIDI_INPUTS["instruments"]))]
        # pprint(self.notes)
        # create a track for our midi file
        self.midi = MIDIFile(1, eventtime_is_ticks=True, ticks_per_quarternote=4)
        # set the tempo of the midi file
        self.midi.addTempo(0, 0, 120)
        for track, notes in enumerate(self.notes):
            # set the instrument of the midi file
            self.midi.addProgramChange(0, 0, 0, MIDI_INPUTS["instruments"][track])
            # add the notes to the midi file
            total_time = 0
            for note in notes:
                # based on out note information (pitch, duration, velocity) generate a note
                # (track, channel, pitch, time, duration, volume)
                # click.echo(f"Adding note: {note}; total_time: {total_time}")
                self.midi.addNote(0, 0, note[0], total_time, note[1], note[2])
                total_time += note[1]

    def save_wav_file(self, t_id=None):
        """Save the midi file"""
        filename = t_id or "".join(random.choices(string.ascii_letters, k=10))
        with open(f"{filename}.mid", "wb") as output_file:
            self.midi.writeFile(output_file)
        # convert the midi file to a wav file
        # f"fluidsynth -F {filename}.wav {filename}.mid"
        os.popen(f"fluidsynth -F {filename}.wav {filename}.mid")
        time.sleep(1)
        # subprocess.call(f"fluidsynth -F {filename}.wav {filename}.mid")
        # import sys; sys.exit()
        # remove the midi file
        os.remove(f"{filename}.mid")
        return f"{filename}.wav"


class MidiLearner:
    """A class that controls the midi populations and learning process."""

    def __init__(self, generations, pop_total, mutation_chance=0.1):
        self.generations = generations
        self.pop_total = pop_total
        self.mutation_chance = mutation_chance
        self.population = Population(
            population_count=self.pop_total,
            rev_pop_sort=False,
            generator_function=MidiLearner.generate_genes,
        )

    @staticmethod
    def generate_genes():
        # instrument, effect, num_notes, pitch_range, pitch_variability, duration_range, duration_variability, velicity_range, velocity_variability
        return [
            random.choice(MIDI_INPUTS["effects"]),
            random.randint(1, 5),
            random.randint(1, 10),
            random.random(),
            random.randint(1, 10),
            random.random(),
            random.randint(64, 127),
            random.random(),
        ]

    def user_track_rating(self, tracks):
        """given a mapping of organism to track, prompt the user to listen to and rate the tracks"""
        click.secho(
            "Please choose a track to listen and select the top 3 organisms by id",
            fg="green",
        )
        org_id_map = {i: org for i, org in enumerate(tracks.keys())}
        # prompt the user to rate the top 3 tracks in a space separated list
        user_ratings = click.prompt("Enter the top 3 organisms by id").split()
        # split the input into a list of organisms
        user_ratings = [org_id_map[int(i)] for i in user_ratings]
        return user_ratings

    def run(self):
        click.secho("Starting midi learner", fg="green")
        for i in range(self.generations):
            click.secho(f"Starting generation {i}", fg="green")
            # generate the midi tracks
            curr_tracks = {}
            for i, organism in enumerate(self.population.population):
                curr_tracks[organism] = organism.generate_song(t_id=i, duration=30)
            # get the fitness of the tracks
            ratings = self.user_track_rating(curr_tracks)
            ratings[0].points = 3
            ratings[1].points = 2
            ratings[2].points = 1
            # sort the population by fitness
            self.population.sort_population()
            # tell the user the best track
            click.secho(f"The best track was {curr_tracks[ratings[0]]}", fg="green")
            # ask to proceed to next generation
            click.secho("Proceed to next generation? [y/n]", fg="green")
            # clean up the tracks
            for track in curr_tracks.values():
                os.remove(track)
            if input() == "n":
                ratings[0].generate_song(t_id="the_best_around", duration=3000)
                break
            # create the next generation
            self.population.breed_population()


@click.command()
@click.option(
    "--generations",
    default=10,
    help="The number of generations to run the midi learner for",
)
@click.option(
    "--pop-total", default=10, help="The total number of organisms in the population"
)
@click.option(
    "--mutation-chance", default=0.1, help="The chance of a mutation occuring"
)
def main(generations, pop_total, mutation_chance):
    midi_learner = MidiLearner(generations, pop_total, mutation_chance)
    midi_learner.run()


if __name__ == "__main__":
    main()


# test api version of broker settings stuff
# create an initial population of organisms with genes representing
# permutations of MIDI_INPUTS
# 8 5 9