"""
This is a script that uses genetic algortihms to generate midi music.
The user then votes on the top 3 of 10 randomly generated songs.
The top 3 songs are then used to generate the next generation of songs.
"""
import os
from pathlib import Path
from pprint import pprint
import random
import string
import time
from collections import deque
import click
import numpy as np
from pydub import AudioSegment
from midiutil.MidiFile import MIDIFile


MIDI_INPUTS = {
    "effects": ["reverb", "delay", "chorus"],
}


class Population:
    """This class is the controller for the population of Orgamisms."""

    def __init__(
        self,
        top_generator_function,
        track_generator_function,
        population_count=20,
        population=None,
        rev_pop_sort=False,
        mutate=True,
    ):
        self.top_generator_function = top_generator_function
        self.track_generator_function = track_generator_function
        self.population_count = population_count
        self.population = population or []
        self.rev_pop_sort = rev_pop_sort
        self.mutate = mutate
        self._generate_population()

    def _generate_population(self):
        """Generate a population of organisms."""
        self.population = []
        for _ in range(self.population_count):
            org = Organism(
                top_func=self.top_generator_function,
                track_func=self.track_generator_function,
            )
            self.population.append(org)

    def _breed_pair(self, gene_list1, gene_list2):
        """Breed two gene lists together.

        The first has a greater chance of passing their genes on.
        Random mutation is then given a chance to change the child.

        """
        new_gene_list = []
        if gene_list1 and gene_list2:
            # If we have nested genes, then recursively breed them
            # mix top-level items
            crossover = random.randint(0, len(gene_list1))
            new_gene_list.append(
                gene_list1[0][:crossover] + gene_list2[0][crossover:]
            )  # instruments
            new_gene_list.append(random.choice([gene_list1[1], gene_list2[1]]))  # seed
            new_gene_list.append(
                random.choice([gene_list1[2], gene_list2[2]])
            )  # duration
            # mix tracks
            crossover = random.randint(0, min((len(gene_list1[3]), len(gene_list2[3]))))
            new_gene_list.append(
                gene_list1[3][:crossover] + gene_list2[3][crossover:]
            )  # tracks
            # if there aren't enough tracks, add in ones not included
            while len(new_gene_list[3]) < len(new_gene_list[0]):
                new_gene_list[3].append(
                    random.choice(gene_list1[3][crossover:] + gene_list2[3][:crossover])
                )
            # if there are too many tracks, cap them off
            new_gene_list[3] = new_gene_list[3][: len(new_gene_list[0])]
        else:
            new_gene_list = gene_list1
        return new_gene_list

    def breed_population(self, pool_percentage=50):
        """ "Cross breed the population with only the top percentage.

        :param pool_percentage: Percentage defines primary breeder cutoff.

        """
        # Create the breeding order. Those on top get more iterations.
        self.sort_population()
        # check for stagnation
        if self.population[0].points == self.population[-1].points:
            click.secho("Stagnation detected! Incrasing mutation chance.", fg="yellow")
            mutation_chance = 0.9
        else:
            mutation_chance = 0.3

        breeders = self.population[
            : int(self.population_count * (float(pool_percentage) / 100))
        ]
        # Add in some random members of the population
        while self.population_count > len(breeders):
            breeders.append(random.choice(self.population))

        next_generation = [
            Organism(
                genes=breeders[0].genes[:],
                top_func=self.top_generator_function,
                track_func=self.track_generator_function,
            )
        ]  # keep our best

        # Breed the population
        while len(next_generation) < self.population_count:
            # use weighted choice to select breeding pairs
            org1, org2 = random.choices(
                breeders, k=2, weights=[org.points for org in breeders]
            )
            if org1 != org2:
                new_org = Organism(
                    genes=self._breed_pair(org1.genes, org2.genes),
                    top_func=self.top_generator_function,
                    track_func=self.track_generator_function,
                )
            else:  # Avoid potential stagnation by introducing a new organism
                new_org = Organism(
                    top_func=self.top_generator_function,
                    track_func=self.track_generator_function,
                )
            next_generation.append(new_org)
        self.population = next_generation

        # Randomly mutate our new population
        if self.mutate:
            for org in self.population[1:]:  # skip our best
                if random.random() <= mutation_chance:
                    org.mutate()

    def sort_population(self, reverse=None):
        """Sort the population by the number of points they have."""
        reverse = reverse or self.rev_pop_sort
        self.population = sorted(
            self.population, key=lambda org: org.points, reverse=reverse
        )


class Organism:
    def __init__(self, genes=None, top_func=None, track_func=None, points=0):
        self.top_func = top_func
        self.track_func = track_func
        if not genes:
            self.generate_genes()
        else:
            self.genes = genes
        self.points = points

    def _get_genes(self):
        return self.instruments, self.track_seed, self.duration, self.tracks

    def _set_genes(self, genes):
        self.instruments, self.track_seed, self.duration, self.tracks = genes

    genes = property(_get_genes, _set_genes)

    def _generate_track(self):
        return self.track_func(self.track_seed, self.duration)

    def generate_genes(self):
        """Randomly sort the genes to provide different combinations."""
        self.instruments, self.track_seed, self.duration = self.top_func()
        self.tracks = [self._generate_track() for _ in range(len(self.instruments))]

    def mutate(self):
        """Randomly mutate the genes, if dice rolls pass"""
        # give each gene a chance to mutate
        mutated_top = self.top_func()
        new_instruments = self.instruments.copy()
        for pos in range(len(self.instruments)):
            if random.random() <= 0.3:
               new_instruments[pos] = random.choice(mutated_top[0])
        if random.random() <= 0.3:
            self.track_seed = mutated_top[1]
        if random.random() <= 0.3:
            self.duration = mutated_top[2]
        if len(new_instruments) > len(self.instruments):
            self.tracks.extend(
                [
                    self._generate_track()
                    for _ in range(len(new_instruments) - len(self.instruments))
                ]
            )
        elif len(new_instruments) < len(self.instruments):
            self.tracks = self.tracks[: len(new_instruments)]
        self.instruments = new_instruments
        # mutate the track genes
        for pos in range(len(self.tracks)):
            if random.random() <= 0.3:
                new_track = self._generate_track()
                crossover = random.randint(0, len(new_track))
                self.tracks[pos] = self.tracks[pos][:crossover] + new_track[crossover:]

    def generate_song(self, t_id=None, duration=300):
        """Generate a song from the genes."""
        song = MidiSong(
            instruments=self.instruments,
            duration=duration or self.duration,
            tracks=self.tracks,
        )
        song.generate_midi_file()
        try:
            return song.save_wav_file(t_id=t_id)
        except Exception as e:
            click.secho(f"Error saving wav file: {e}", fg="red")
            return f"{t_id}.mid"

    def __repr__(self):
        return f"Organism({self.instruments=}, {self.track_seed=}, {self.duration=}, {self.points=})"


class MidiSong:
    def __init__(
        self,
        instruments,
        duration,
        tracks=None,
    ):
        self.instruments = instruments or []
        self.duration = duration
        self.tracks = tracks or []

    def generate_midi_file(self):
        """Generate a midi file"""
        # pprint(self.notes)
        # create a track for our midi file
        self.midi = MIDIFile(1, eventtime_is_ticks=True, ticks_per_quarternote=4, deinterleave=False)
        # set the tempo of the midi file
        self.midi.addTempo(0, 0, 120)
        for pos, notes in enumerate(self.tracks):
            # set the instrument of the midi file
            self.midi.addProgramChange(0, 0, 0, self.instruments[pos])
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
        time.sleep(2)
        # subprocess.call(f"fluidsynth -F {filename}.wav {filename}.mid")
        # import sys; sys.exit()
        # remove the midi file
        os.remove(f"{filename}.mid")
        return f"{filename}.wav"


class MidiLearner:
    """A class that controls the midi populations and learning process."""

    def __init__(self, goal_song, generations, pop_total, mutation_chance=0.1, ask_user=False):
        self.goal_song = goal_song
        self.generations = generations
        self.pop_total = pop_total
        self.mutation_chance = mutation_chance
        self.ask_user = False
        self.population = Population(
            population_count=self.pop_total,
            rev_pop_sort=False,
            top_generator_function=MidiLearner.generate_genes,
            track_generator_function=MidiLearner.generate_notes,
        )

    @staticmethod
    def generate_genes():
        return [
            [random.randint(0, 127) for _ in range(random.randint(1, 10))],  # instrumets
            {  # track seed
                "pitch_range": random.randint(1, 10),
                "pitch_variability": random.random(),
                "duration_range": random.randint(1, 10),
                "duration_variability": random.random(),
                "velocity_range": random.randint(64, 127),
                "velocity_variability": random.random(),
            },
            random.randint(60, 1000),  # duration
        ]

    @staticmethod
    def generate_notes(track_seed, duration=300):
        """Generate a series of notes that equates to a duration"""
        _cur_note = random.randint(0, 128)
        _cur_duration = 4
        _cur_velocity = 75
        _total_duration = 0
        notes = []
        while _total_duration < duration:
            # roll the dice to determine if we change the pitch
            if random.random() < track_seed["pitch_variability"]:
                # if so, choice a note within range of the current note based on pitch_range
                _cur_note = random.randint(
                    _cur_note - track_seed["pitch_range"],
                    _cur_note + track_seed["pitch_range"],
                )
                # ensure the note is between 0 and 128
                if _cur_note < 0:
                    _cur_note = 0
                elif _cur_note > 128:
                    _cur_note = 128
            # roll the dice to determine if we change the duration
            if random.random() < track_seed["duration_variability"]:
                # if so choose a duration that is within range of the current duration based on duration_range
                _cur_duration = random.randint(
                    _cur_duration - track_seed["duration_range"],
                    _cur_duration + track_seed["duration_range"],
                )
                # ensure the note duration is at least 1
                if _cur_duration < 1:
                    _cur_duration = 1
            # roll the dice to determine if we change the velocity
            if random.random() < track_seed["velocity_variability"]:
                # if so choose a velocity that is within range of the current velocity based on velocity_range
                _cur_velocity = random.randrange(
                    _cur_velocity - track_seed["velocity_range"],
                    _cur_velocity + track_seed["velocity_range"],
                )
                # ensure the velocity is between 64 and 127
                if _cur_velocity < 64:
                    _cur_velocity = 64
                elif _cur_velocity > 127:
                    _cur_velocity = 127
            # add the note to the notes list
            notes.append([_cur_note, _cur_duration, _cur_velocity])
            _total_duration += _cur_duration
        return notes

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
        self.goal_song = AudioSegment.from_wav(self.goal_song)
        self.goal_song = np.array(self.goal_song.get_array_of_samples())
        goal_norm = self.goal_song / np.linalg.norm(self.goal_song)
        len_goal_song = len(self.goal_song)
        best = None
        for i in range(self.generations):
            click.secho(f"Starting generation {i}", fg="green")
            # generate the midi tracks
            for i, organism in enumerate(self.population.population):
                generated = organism.generate_song(t_id=i, duration=30)
                if (gen_path := Path(generated)).exists() and generated.endswith(
                    ".wav"
                ):
                    # create an np array of the generated track
                    generated = AudioSegment.from_wav(generated)
                    generated = np.array(generated.get_array_of_samples())
                    # calculate the size difference between the goal and generated track
                    size_diff = abs(len_goal_song - len(generated))
                    # normalize the arrays to the same size
                    if len_goal_song > len(generated):
                        generated = np.pad(generated, (0, size_diff), "constant")
                    elif len_goal_song < len(generated):
                        generated = generated[:len_goal_song]
                    generated_norm = generated / np.linalg.norm(generated)
                    # calculate the difference between the two tracks
                    # diff = int(np.linalg.norm(self.goal_song - generated, ))
                    try:
                        diff = int((1 - abs(np.dot(goal_norm, generated_norm))) * 100000)
                    except ValueError:
                        diff = 99999999
                    organism.points = diff + size_diff
                    gen_path.unlink()
                elif gen_path.exists():
                    gen_path.unlink()
                    organism.points = 90000000
                else:
                    organism.points = 99999999

            # sort the population by fitness
            self.population.sort_population()
            # tell the user the best track
            click.secho(
                f"The best song score was {self.population.population[0].points}",
                fg="green",
            )
            if self.ask_user:
                # ask to proceed to next generation
                click.secho("Proceed to next generation? [y/n]", fg="green")
                if input() == "n":
                    self.population.population[0].generate_song(t_id="the_best_around")
                    break
            # create the next generation
            os.popen("killall fluidsynth")
            if not best or best.points > self.population.population[0].points:
                best = self.population.population[0]
            self.population.breed_population()
        click.secho(f"Finished midi learner. Best organism was {best}", fg="green")
        best.generate_song(t_id="the_best_around")


@click.command()
@click.option("--goal-song", help="The path to the goal song to learn")
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
@click.option(
    "--ask-before-next-gen",
    default=False,
    help="Ask the user if they want to proceed to the next generation",
)
def main(goal_song, generations, pop_total, mutation_chance, ask_before_next_gen):
    midi_learner = MidiLearner(goal_song, generations, pop_total, mutation_chance, ask_before_next_gen)
    midi_learner.run()


if __name__ == "__main__":
    try:
        main()
    except:
        os.popen("killall fluidsynth")
        raise

# test api version of broker settings stuff
