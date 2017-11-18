"""
Use a Genetic Algorithm to reproduce an image by pixel or polygon.

requires: python 3, attrs, pillow
top area for improvement: multi-thread organism scoring.
"""

import argparse, attr, random
from collections import deque
from PIL import Image, ImageDraw


@attr.s()
class Population(object):
    """This class is the controller for the population of Orgamisms."""

    gene_base = attr.ib(
        validator=attr.validators.instance_of(list), cmp=False, repr=False)
    population_count = attr.ib(default=20)
    population = attr.ib(default=attr.Factory(list), cmp=False)
    top_scores = attr.ib(default=deque(maxlen=200), repr=False)
    rev_pop_sort = attr.ib(default=False, cmp=False, repr=False)
    generator_function = attr.ib(default=False, cmp=False, repr=False)
    gene_length = attr.ib(default=False, cmp=False, repr=False)
    mutate = attr.ib(default=True, cmp=False, repr=False)

    def __attrs_post_init__(self):
        """Generate a population of organisms."""
        self.population = []
        for _ in range(self.population_count):
            org = Organism(genes=self.gene_base[:])
            org.generate_genes(
                gen_func=self.generator_function, count=self.gene_length)
            self.population.append(org)

    def _breed_pair(self, gene_list1, gene_list2):
        """Breed two gene lists together.

        The first has a greater chance of passing their genes on.
        Random mutation is then given a chance to change the child.

        """
        new_gene_list = []
        # If we have nested genes, then recursively breed them
        if isinstance(gene_list1[0], list):
            for list1, list2 in zip(gene_list1, gene_list2):
                new_gene_list.append(self._breed_pair(list1, list2))
        else:
            crossover = random.randint(0, len(gene_list1))
            new_gene_list = gene_list1[:crossover]
            new_gene_list.extend(gene_list2[crossover:])
        return new_gene_list

    def breed_population(self, pool_percentage=50):
        """"Cross breed the population with only the top percentage.

        :param pool_percentage: Percentage defines primary breeder cutoff.

        """
        # Create the breeding order. Those on top get more iterations.
        self.sort_population()
        breeders = self.population[
            :int(self.population_count * (float(pool_percentage) / 100))
        ]
        self.top_scores.append(breeders[0].points)
        # Add in some random members of the population
        while self.population_count > len(breeders):
            breeders.append(random.choice(self.population))

        next_generation = [Organism(genes=breeders[0].genes[:])]  # keep our best
        # Randomly mutate our existing population
        if self.mutate:
            if len(self.top_scores) == 200 and self.top_scores[0] == self.top_scores[-1]:
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
                    new_org = Organism(genes=self._breed_pair(org1.genes, org2.genes))
            else:  # Avoid potential stagnation by introducing a new organism
                new_org = Organism(genes=self.gene_base[:])
                new_org.generate_genes(
                    gen_func=self.generator_function, count=self.gene_length)
            next_generation.append(new_org)
        self.population = next_generation

    def sort_population(self, reverse=None):
        """Sort the population by the number of points they have."""
        reverse = reverse or self.rev_pop_sort
        self.population = sorted(
            self.population, key=lambda org: org.points, reverse=reverse)

@attr.s(slots=True)
class Organism(object):
    """The is the actor class that is the target of evolution."""

    genes = attr.ib(validator=attr.validators.instance_of(list), cmp=False)
    points = attr.ib(default=0)

    def generate_genes(self, gen_func=None, count=None):
        """Randomly sort the genes to provide different combinations."""
        if gen_func and count:
            self.genes = [gen_func() for _ in range(count)]
        if isinstance(self.genes[0], list):
            for i in range(len(self.genes)):
                self.genes[i] = self.genes[i][:]
                random.shuffle(self.genes[i])
        else:
            self.genes = self.genes[:]
            random.shuffle(self.genes)

    def mutate(self, gene_base=None):
        """Randomly mutate the list by swapping two genes around."""
        gene_base = gene_base or self.genes
        if isinstance(self.genes[0], list):
            for i in range(len(self.genes)):
                if random.random() < 0.1:
                        gene1 = random.choice(range(len(self.genes[i])))
                        gene2 = random.choice(range(len(self.genes[i])))
                        self.genes[i][gene1], self.genes[i][gene2] = (
                            self.genes[i][gene2], self.genes[i][gene1])
                else:  # Or we'll mutate to have a new/duplicate value introduced
                    self.genes[i][
                        random.randint(0, len(self.genes[i]) - 1)
                    ] = random.choice(self.genes[i])
        else:
            if random.random() < 0.1:
                    gene1 = random.choice(range(len(self.genes)))
                    gene2 = random.choice(range(len(self.genes)))
                    self.genes[gene1], self.genes[gene2] = (
                        self.genes[gene2], self.genes[gene1])
            else:  # Or we'll mutate to have a new/duplicate value introduced
                genes = gene_base or self.genes
                self.genes[
                    random.randint(0, len(self.genes) - 1)
                ] = random.choice(genes)


def fill_pic(im, pixel_list):
    for x in range(im.width):
        buff = pixel_list[:im.height]
        pixel_list = pixel_list[im.height:]
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
    return total ** 2

def judge_poly(target, actual):
    actual_list = get_pixel_list(actual)
    return judge_org(actual_list, target)

def make_poly(max_x, max_y, mode, point_count=3):
    poly = [random.randint(0, max_x), random.randint(0, max_y)]  # poly size
    poly.extend([random.randint(0, max_x - poly[0]), random.randint(0, max_y - poly[1])])  # poly position
    if point_count == 1:
        poly.append(random.randint(0, min(poly[0], poly[1])))
    else:
        for i in range(point_count):
            poly.extend([random.randint(0, poly[0]), random.randint(0, poly[1])])  # poly point
    for i in range(len(mode) + 1):
        poly.append(random.randint(0, 255))  # poly fill color
    return poly

def draw_org(im, org, point_count=3):
    if point_count > 0:
        base = Image.new(im.mode, im.size, 'Black')
        for poly in org.genes:
            draw_poly(base, poly, point_count)
    else:
        base = Image.new(im.mode, im.size, 'White')
        draw_lines(base, org.genes)
    return base

def draw_poly(base, inlist, point_count):
    poly = Image.new('RGBA', (inlist[0], inlist[1]))
    pdraw = ImageDraw.Draw(poly)
    if point_count > 2:  # not a circle
        position = 4
        poly_list = []
        while point_count > 0:
            poly_list.extend([inlist[position], inlist[position + 1]])
            position += 2
            point_count -= 1
        pdraw.polygon(poly_list, fill=tuple(inlist[position:]))
    elif point_count == 2:
        pdraw.ellipse((0, 0, inlist[4], inlist[5]), fill=tuple(inlist[6:]))
    else:
        pdraw.ellipse((0, 0, inlist[4], inlist[4]), fill=tuple(inlist[5:]))
    poly_offset = (inlist[2], inlist[3])
    base.paste(poly, poly_offset, mask=poly)

def draw_lines(base, inlist):
    ldraw = ImageDraw.Draw(base)
    ldraw.line((inlist[0], inlist[1], inlist[-2], inlist[-1]), width=1, fill=tuple([0] * len(base.mode)))
    for i in range(2, len(inlist), 2):
        ldraw.line((inlist[i], inlist[i + 1], inlist[i - 2], inlist[i - 1]), width=1, fill=tuple([0] * len(base.mode)))

def ga_poly_image(f_path, population=20, polygon_count=20, point_count=3, max_generations=15000, skip=100):
    im = Image.open(f_path)
    target = get_pixel_list(im)
    if point_count > 0:
        gen_fun = lambda: make_poly(im.width, im.height, im.mode, point_count)
    else:
        gen_fun = lambda: random.randint(0, im.width)
    mypop = Population(
        gene_base=target, population_count=population, generator_function=gen_fun,
        gene_length=polygon_count, mutate=False)
    for i in range(max_generations + 1):
        print("Generation: {}".format(i))
        for c in range(population):
            mypop.population[c].points = judge_poly(target, draw_org(im, mypop.population[c], point_count))
        if not i % skip:
            mypop.sort_population()
            print("Generating image {}".format(i))
            draw_org(
                im, mypop.population[0], point_count
            ).convert('RGB').save('output/{}.png'.format(i))
        mypop.breed_population()

def ga_pixel_image(f_path, population=20, max_generations=15000, skip=100):
    im = Image.open(f_path)
    target = get_pixel_list(im)
    if isinstance(target[0], int):
        genfun = lambda: random.randint(0, 255)
    else:
        genfun = lambda: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    mypop = Population(gene_base=target, population_count=population, generator_function=genfun, gene_length=len(target))
    for i in range(max_generations):
        print("Generation: {}".format(i))
        for c in range(population):
            mypop.population[c].points = judge_org(mypop.population[c].genes, target)
        if not i % skip:
            mypop.sort_population()
            print("Generating image {}".format(i))
            im = fill_pic(im, mypop.population[0].genes)
            im.save('output/{}.jpg'.format(i))
        mypop.breed_population()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str,
        help='The path to the image. Larger images will take much longer.')
    subparsers = parser.add_subparsers(dest='command',
        help='"poly" will attempt to match an image with polygons/cricles.lines.\n'
             '"pixel" will attempt to match the individual pixel values of an image.')

    poly = subparsers.add_parser('poly')
    poly.add_argument('--population-count', type=int,
        help='The number of organisms in each generation. Recommend betwen 20-100.')
    poly.add_argument('--polygons', type=int,
        help='The number of polygons used to recreate the image. Recommend betwen 20-200')
    poly.add_argument('--points', type=int,
        help='The number of points per polygon. 0 will draw lines, 1 is circle, 2 is ovals, '
             '3+ will make traditional polygons.')
    poly.add_argument('--generations', type=int,
        help='The number of generations to run. Recommend at least 10000 for decent results.')
    poly.add_argument('--skip', type=int,
        help='The generations to skip between image outputs. Recommend 100.')

    pixel = subparsers.add_parser('pixel')
    pixel.add_argument('--population-count', type=int,
        help='The number of organisms in each generation. Recommend betwen 20-100.')
    pixel.add_argument('--generations', type=int,
        help='The number of generations to run. Recommend at least 10000 for decent results.')
    pixel.add_argument('--skip', type=int,
        help='The generations to skip between image outputs. Recommend 100.')

    args = parser.parse_args()

    if args.command == 'poly':
        print('Starting polygon-based image recreation. This will take a long time...')
        ga_poly_image(args.path,
                      args.population_count if args.population_count else 20,
                      args.polygons if args.polygons else 20,
                      args.points if args.points else 3,
                      args.generations if args.generations else 15000,
                      args.skip if args.skip else 100
        )
    else:
        print('Starting pixel-based image recreation. This will take a long time...')
        ga_pixel_image(args.path,
                      args.population_count if args.population_count else 20,
                      args.generations if args.generations else 15000,
                      args.skip if args.skip else 100
        )
    print('Done!')