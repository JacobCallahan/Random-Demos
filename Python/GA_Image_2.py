"""
Use a Genetic Algorithm to reproduce an image by pixel or polygon.

requires: python 3, attrs, pillow
top area for improvement: multi-thread organism scoring.
"""

import argparse, attr, random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import deque
from PIL import Image, ImageDraw
import numpy as np


WEIGHTED_CROSSOVER_RATE = 0.7
BASE_MUT_CHANCE = 0.05
BASE_KEEP_CHANCE = 0.9
TOUGH_MUT_CHANCE = 0.1
TOUGH_KEEP_CHANCE = 0.8
EXTREME_MUT_CHANCE = 0.2
EXTREME_KEEP_CHANCE = 0.7
COORD_MUT_CHANCE = 0.15
INTERGEN_STAG_THRESHOLD = 0.95
INTRAGEN_STAG_THRESHOLD = 0.9


@attr.s(slots=True)
class Polygon:
    max_x = attr.ib(default=None)
    max_y = attr.ib(default=None)
    point_count = attr.ib(default=3)
    width = attr.ib(default=None)
    height = attr.ib(default=None)
    x_pos = attr.ib(default=None)
    y_pos = attr.ib(default=None)
    coordinates = attr.ib(default=None)
    color = attr.ib(default=None)
    _skip_post = attr.ib(default=False, cmp=False, repr=False)

    def __attrs_post_init__(self):
        if self._skip_post:
            return
        self.width = random.randrange(3, self.max_x + 1)
        self.height = random.randrange(3, self.max_y + 1)
        if self.point_count == 1:
            # drawing a circle, normalize the size to be square
            self.width = self.height = min(self.width, self.height)
        self.x_pos = random.randrange(0, self.max_x - self.width + 1)
        self.y_pos = random.randrange(0, self.max_y - self.height + 1)
        self.coordinates = []
        if self.point_count == 1:
            # circle uses the width as the radius
            self.coordinates.append(self.width)
        else:
            for _ in range(self.point_count):
                # generate random points within the bounds
                self.coordinates.append(random.randrange(self.width + 1))
                self.coordinates.append(random.randrange(self.height + 1))
        # print(f"{poly_width=}, {x_mid=}, {max_x_reach=}, actual_reach={poly[-1]}")
        self.color = tuple(random.randrange(256) for _ in range(4))

    def get_poly(self):
        return [
            self.width,
            self.height,
            self.x_pos,
            self.y_pos,
            *self.coordinates,
            *self.color,
        ]

    def change_size(self, new_width, new_height):
        # determine the difference between the new and old size
        width_diff = new_width - self.width
        height_diff = new_height - self.height
        # set the new size
        self.width = new_width
        self.height = new_height
        # adjust our position to the new size
        self.change_position(self.x_pos, self.y_pos)
        # adjust the coordinates to the new size
        if self.point_count == 1:
            self.coordinates = [new_width]
            return
        for i in range(0, len(self.coordinates), 2):
            self.coordinates[i] += width_diff
            self.coordinates[i + 1] += height_diff

    def change_position(self, new_x, new_y):
        self.x_pos = new_x
        self.y_pos = new_y
        if self.x_pos + self.width > self.max_x:
            self.x_pos = self.max_x - self.width
        if self.y_pos + self.height > self.max_y:
            self.y_pos = self.max_y - self.height

    def change_coordinate(self, index, new_value):
        # ensure the new value is within our bounds
        if index % 2 == 0:
            # x coordinate
            if new_value > self.width:
                new_value = self.width
        else:
            # y coordinate
            if new_value > self.height:
                new_value = self.height
        self.coordinates[index] = new_value

    def _from_poly(self, full_copy=False):
        # create a new polygon based on our image constraints
        if not full_copy:
            return Polygon(self.max_x, self.max_y, self.point_count)
        else:
            return Polygon(
                self.max_x,
                self.max_y,
                self.point_count,
                self.width,
                self.height,
                self.x_pos,
                self.y_pos,
                self.coordinates[:],
                self.color,
                True,
            )

    def weighted_crossover(self, other):
        """This is a weighted crossover function."""
        clone = self._from_poly(full_copy=True)
        # chance a size mutation
        if random.random() < WEIGHTED_CROSSOVER_RATE:
            clone.change_size(other.width, other.height)
        # chance a position mutation
        if random.random() < WEIGHTED_CROSSOVER_RATE:
            clone.change_position(other.x_pos, other.y_pos)
        # chance a color mutation
        if random.random() < WEIGHTED_CROSSOVER_RATE:
            clone.color = other.color
        # chance point mutations
        for i, coord in enumerate(other.coordinates):
            if random.random() < WEIGHTED_CROSSOVER_RATE:
                clone.change_coordinate(i, coord)
        if not clone.validate():
            import IPython

            IPython.embed()
        return clone

    def validate(self):
        """Check that all coordinates are within the bound of the polygon.
        And that the polygon fits within the image.
        """
        if self.point_count == 1:
            return True
        for i in range(0, len(self.coordinates), 2):
            if (
                self.coordinates[i] > self.width
                or self.coordinates[i + 1] > self.height
            ):
                print(f"Failing at cordinate pairs {i=} and +1")
                return False
        if (
            self.x_pos + self.width > self.max_x
            or self.y_pos + self.height > self.max_y
        ):
            print("Failing at positioning")
            return False
        return True


@attr.s()
class Population:
    """This class is the controller for the population of Orgamisms."""

    population_count = attr.ib(default=20)
    population = attr.ib(default=attr.Factory(list), cmp=False)
    top_scores = attr.ib(default=None, repr=False)
    rev_pop_sort = attr.ib(default=False, cmp=False, repr=False)
    generator_function = attr.ib(default=False, cmp=False, repr=False)
    gene_length = attr.ib(default=False, cmp=False, repr=False)
    mutate = attr.ib(default=True, cmp=False, repr=False)

    def __attrs_post_init__(self):
        """Generate a population of organisms."""
        self.population = []
        self.top_scores = deque(maxlen=200)
        for _ in range(self.population_count):
            org = Organism(genes=[])
            org.generate_genes(gen_func=self.generator_function, count=self.gene_length)
            self.population.append(org)

    def _breed_pair(self, genes1, genes2):
        # single point crossover
        # crossover = random.randint(0, len(gene_list1))
        # new_gene_list = gene_list1[:crossover]
        # new_gene_list.extend(gene_list2[crossover:])
        # uniform crossover
        # return [gene_poly1 + gene_poly2 for gene_poly1, gene_poly2 in zip(genes1, genes2)]
        # weighted crossover
        return [
            gene_poly1.weighted_crossover(gene_poly2)
            for gene_poly1, gene_poly2 in zip(genes1, genes2)
        ]

    def breed_population(self, pool_percentage=50):
        """ "Cross breed the population with only the top percentage.

        :param pool_percentage: Percentage defines primary breeder cutoff.

        """
        # Create the breeding order. Those on top get more iterations.
        self.sort_population()
        self.top_scores.append(self.population[0].points)
        # check for stagnation
        if len(self.top_scores) == 200 and self.top_scores[-1] >= self.top_scores[0]:
            print(f"Terminal stagnation detected! Exiting.")
            sys.exit()
        elif (
            len(self.top_scores) == 200
            and self.top_scores[-1] <= self.top_scores[0] * INTERGEN_STAG_THRESHOLD
        ):
            print("Inter-generational stagnation detected! Increasing mutation chance.")
            mutation_chance = EXTREME_MUT_CHANCE
            keep_chance = EXTREME_KEEP_CHANCE
        elif (
            len(self.top_scores) >= 100
            and self.population[0].points >= self.population[-1].points * INTRAGEN_STAG_THRESHOLD
        ):
            print("Intra-generational stagnation detected! Increasing mutation chance.")
            mutation_chance = TOUGH_MUT_CHANCE
            keep_chance = TOUGH_KEEP_CHANCE
        else:
            mutation_chance = BASE_MUT_CHANCE
            keep_chance = BASE_KEEP_CHANCE

        breeders = self.population[
            : int(self.population_count * (float(pool_percentage) / 100))
        ]
        # Add in some random members of the population
        while self.population_count * keep_chance > len(breeders):
            breeders.append(random.choice(self.population))

        # Breed the population
        next_generation = [Organism(genes=breeders[0].genes[:])]  # keep our best
        # the higher the mutation chance, the less population we keep
        while len(next_generation) < self.population_count * keep_chance:
            # random choice with weight toward the front of the list
            org1, org2 = random.choices(
                breeders, k=2, weights=range(len(breeders), 0, -1)
            )
            # org1 = random.choice(breeders)
            # org2 = random.choice(breeders)
            if org1 != org2:
                new_org = Organism(genes=self._breed_pair(org1.genes, org2.genes))
                next_generation.append(new_org)

        # Randomly mutate next population
        if self.mutate:
            for org in next_generation[1:]:  # skip our best
                if random.random() <= mutation_chance:
                    org.mutate()

        # fill in remaining population with brand new organisms
        while len(next_generation) < self.population_count:
            new_org = Organism(genes=[])
            new_org.generate_genes(
                gen_func=self.generator_function, count=self.gene_length
            )
            next_generation.append(new_org)

        self.population = next_generation

    def sort_population(self, reverse=None):
        """Sort the population by the number of points they have."""
        reverse = reverse or self.rev_pop_sort
        self.population = sorted(
            self.population, key=lambda org: org.points, reverse=reverse
        )


@attr.s(slots=True)
class Organism:
    """The is the actor class that is the target of evolution."""

    genes = attr.ib(validator=attr.validators.instance_of(list), cmp=False)
    points = attr.ib(default=0)

    def generate_genes(self, gen_func=None, count=None):
        """Randomly sort the genes to provide different combinations."""
        if gen_func and count:
            self.genes = [gen_func() for _ in range(count)]

    def mutate(self, mutation_chance=BASE_MUT_CHANCE):
        """Randomly mutate the gene list"""
        # calculate the weight based on the gene length to attempt to
        # reach a possible 100% chance over all genes
        _mut_chance = mutation_chance / len(self.genes)
        for i in range(len((self.genes))):
            mutant_poly = self.genes[i]._from_poly()
            # chance a size mutation
            if random.random() < mutation_chance:
                self.genes[i].change_size(mutant_poly.width, mutant_poly.height)
            # chance a position mutation
            if random.random() < mutation_chance:
                self.genes[i].change_position(mutant_poly.x_pos, mutant_poly.y_pos)
            # chance a color mutation
            if random.random() < mutation_chance:
                self.genes[i].color = mutant_poly.color
            # chance point mutations
            _point_mut_chance = COORD_MUT_CHANCE / len(self.genes[i].coordinates)
            for i, coord in enumerate(mutant_poly.coordinates):
                if random.random() < _point_mut_chance:
                    self.genes[i].change_coordinate(i, coord)
            if not self.genes[i].validate():
                import IPython

                IPython.embed()


def fill_pic(im, pixel_list):
    for x in range(im.width):
        buff = pixel_list[: im.height]
        pixel_list = pixel_list[im.height :]
        for y in range(im.height):
            im.putpixel((x, y), buff.pop(0))
    return im


def get_pixel_list(im):
    pixel_list = []
    for x in range(im.width):
        for y in range(im.height):
            pixel_list.append(im.getpixel((x, y)))
    return pixel_list


def judge_pixel(expected, received):
    total = 0
    for i in range(len(expected)):
        total += abs(expected[i] - received[i])
    return total


def judge_org(genelist, target):
    total = 0
    for i in range(len(genelist)):
        if isinstance(target[i], int):
            total += abs(target[i] - genelist[i])
        else:
            total += judge_pixel(target[i], genelist[i])
    return total**2


NP_TARGET = None


def np_mse_judge(target, org, org_obj):
    """Convert the list of genes into a numpy array and use MSE to judge."""
    global NP_TARGET
    if NP_TARGET is None:
        NP_TARGET = np.array(target)
    org = np.array(get_pixel_list(org))
    return org_obj, np.mean(np.square(org - NP_TARGET))


def judge_poly(target, actual):
    actual_list = get_pixel_list(actual)
    return judge_org(actual_list, target)


def make_poly(max_x, max_y, mode, point_count=3):
    return Polygon(max_x, max_y, point_count)


def draw_org(im, org, point_count=3):
    if point_count > 0:
        base = Image.new(im.mode, im.size, "Black")
        for poly in org.genes:
            draw_poly(base, poly, point_count)
    else:
        base = Image.new(im.mode, im.size, "White")
        draw_lines(base, org.genes)
    return base


def draw_poly(base, in_poly, point_count):
    poly = Image.new("RGBA", (in_poly.width, in_poly.height))
    pdraw = ImageDraw.Draw(poly)
    if point_count > 2:  # not a circle
        pdraw.polygon(in_poly.coordinates, fill=in_poly.color)
    elif point_count == 2:
        pdraw.ellipse((0, 0, *in_poly.coordinates), fill=in_poly.color)
    else:
        pdraw.ellipse(
            (0, 0, in_poly.coordinates[0], in_poly.coordinates[0]), fill=in_poly.color
        )
        # pdraw.ellipse((0, 0, inlist[4], inlist[4]), fill="Red")
    poly_offset = in_poly.x_pos, in_poly.y_pos
    # poly_offset = (0,0)
    base.paste(poly, poly_offset, mask=poly)


def draw_lines(base, inlist):
    ldraw = ImageDraw.Draw(base)
    ldraw.line(
        (inlist[0], inlist[1], inlist[-2], inlist[-1]),
        width=1,
        fill=tuple([0] * len(base.mode)),
    )
    for i in range(2, len(inlist), 2):
        ldraw.line(
            (inlist[i], inlist[i + 1], inlist[i - 2], inlist[i - 1]),
            width=1,
            fill=tuple([0] * len(base.mode)),
        )


def ga_poly_image(
    f_path,
    population=20,
    polygon_count=20,
    point_count=3,
    max_generations=15000,
    skip=100,
):
    im = Image.open(f_path)
    target = get_pixel_list(im)
    if point_count > 0:
        gen_fun = lambda: make_poly(im.width, im.height, im.mode, point_count)
    else:
        gen_fun = lambda: random.randrange(0, im.width + 1)

    mypop = Population(
        population_count=population,
        generator_function=gen_fun,
        gene_length=polygon_count,
        mutate=True,
    )
    for i in range(max_generations + 1):
        print("Generation: {}".format(i))
        with ProcessPoolExecutor(max_workers=15) as executor:
            tasks = as_completed(
                executor.submit(
                    np_mse_judge, target, draw_org(im, org, point_count), org
                )
                for org in mypop.population
            )
            judge_orgs = []
            for task in tasks:
                res = task.result()
                res[0].points = res[1]
                judge_orgs.append(res[0])
            mypop.population = judge_orgs
        # for c in range(population):
        #     mypop.population[c].points = np_mse_judge(target, draw_org(im, mypop.population[c], point_count))
        if not i % skip:
            mypop.sort_population()
            print(f"Generating image {i}; Best score: {mypop.population[0].points}")
            draw_org(im, mypop.population[0], point_count).convert("RGB").save(
                "output/{}.png".format(i)
            )
        mypop.breed_population()
    return mypop.top_scores[-1]


def ga_pixel_image(f_path, population=20, max_generations=15000, skip=100):
    im = Image.open(f_path)
    target = get_pixel_list(im)
    if isinstance(target[0], int):
        genfun = lambda: random.randrange(256)
    else:
        genfun = lambda: (
            random.randrange(256),
            random.randrange(256),
            random.randrange(256),
        )
    mypop = Population(
        population_count=population, generator_function=genfun, gene_length=len(target)
    )
    for i in range(max_generations):
        print("Generation: {}".format(i))
        for c in range(population):
            mypop.population[c].points = np_mse_judge(mypop.population[c].genes, target)
        if not i % skip:
            mypop.sort_population()
            print("Generating image {}".format(i))
            im = fill_pic(im, mypop.population[0].genes)
            im.save("output/{}.jpg".format(i))
        mypop.breed_population()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        type=str,
        help="The path to the image. Larger images will take much longer.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help='"poly" will attempt to match an image with polygons/cricles.lines.\n'
        '"pixel" will attempt to match the individual pixel values of an image.',
    )

    poly = subparsers.add_parser("poly")
    poly.add_argument(
        "--population-count",
        type=int,
        help="The number of organisms in each generation. Recommend betwen 20-100.",
    )
    poly.add_argument(
        "--polygons",
        type=int,
        help="The number of polygons used to recreate the image. Recommend betwen 20-200",
    )
    poly.add_argument(
        "--points",
        type=int,
        help="The number of points per polygon. 0 will draw lines, 1 is circle, 2 is ovals, "
        "3+ will make traditional polygons.",
    )
    poly.add_argument(
        "--generations",
        type=int,
        help="The number of generations to run. Recommend at least 10000 for decent results.",
    )
    poly.add_argument(
        "--skip",
        type=int,
        help="The generations to skip between image outputs. Recommend 100.",
    )

    pixel = subparsers.add_parser("pixel")
    pixel.add_argument(
        "--population-count",
        type=int,
        help="The number of organisms in each generation. Recommend betwen 20-100.",
    )
    pixel.add_argument(
        "--generations",
        type=int,
        help="The number of generations to run. Recommend at least 10000 for decent results.",
    )
    pixel.add_argument(
        "--skip",
        type=int,
        help="The generations to skip between image outputs. Recommend 100.",
    )

    args = parser.parse_args()

    if args.command == "poly":
        print("Starting polygon-based image recreation. This will take a long time...")
        results = {}
        for rate in range(90, 100):
            INTRAGEN_STAG_THRESHOLD = rate / 100
            print(f"Starting with intergen stag threshold: {INTRAGEN_STAG_THRESHOLD}...")
            score = ga_poly_image(
                args.path,
                args.population_count if args.population_count else 20,
                args.polygons if args.polygons else 20,
                args.points if args.points is not None else 3,
                args.generations if args.generations else 15000,
                args.skip if args.skip else 100,
            )
            results[INTRAGEN_STAG_THRESHOLD] = score
        print(results)
    else:
        print("Starting pixel-based image recreation. This will take a long time...")
        ga_pixel_image(
            args.path,
            args.population_count if args.population_count else 20,
            args.generations if args.generations else 15000,
            args.skip if args.skip else 100,
        )
    print("Done!")
