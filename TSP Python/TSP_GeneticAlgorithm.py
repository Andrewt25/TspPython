import random
import math
import time
import sys
import copy


# read  into infobase dictionary for reference from problem  so city name as key and x and y coordinates as values
def read_infobase(arg):
    try:
        file = open(arg)
    except OSError:
        print(f"Error: could not locate file \"{arg}\"")
    buf = []
    for line in file:
        buf.append(line.rstrip())

    for city in buf:
        city_split = city.split()
        infobase[int(city_split[0])] = [int(city_split[1]), int(city_split[2])]


# generate random route based on given values default to 1 - 1000 if none are supplied
# supply min and max range for partial randomization assumes range either includes first or last item
def random_generation(min_range=0, max_range=None, values=None):
    if values is None:
        values = list(range(1, 1001))
        random.shuffle(values)
    if max_range is None:
        max_range = len(values)
    new_route = []
    if len(values) != (max_range - min_range):
        if min_range != 0:
            front = values[0:min_range]
            end = values[min_range:max_range]
            random.shuffle(end)
            values = front + end
        else:
            front = values[min_range:max_range]
            end = values[max_range:]
            random.shuffle(front)
            values = front + end
    else:
        random.shuffle(values)

    return values


# calculate fitness score using euclidean distance for 1000 city problem with given range for only partial totals
# or entire permutation if no arguments on range given
def fitness_score(route, range_max=None, range_min=0):
    if range_max is None:
        range_max = len(route)
    fitness = 0
    for r in range(range_min, range_max):
        city_one = route[r]
        if r != (range_max - 1):
            city_two = route[r + 1]
        else:
            city_two = route[range_min]
        x_dist = infobase[city_one][0] - infobase[city_two][0]
        y_dist = infobase[city_one][1] - infobase[city_two][1]
        distance_pair = math.sqrt((math.pow(x_dist, 2) + math.pow(y_dist, 2)))
        fitness += distance_pair
    return fitness


# randomly choose two indices then swaps them does this process n times
# a given indice can be swapped more then once returns new list with swapped indices
def random_mutation(route, n):
    working_list = list(route)
    for num in range(n):
        x = random.random()
        y = random.random()
        choices = len(working_list)
        selection_x = math.floor(x * choices)
        selection_y = math.floor(y * choices)
        working_list[selection_x], working_list[selection_y] = working_list[selection_y], working_list[selection_x]

    return working_list


# grabs the n best permutations from current generation
def selection(n, routes):
    sorted_list = sort_by_distance(routes)
    top = []
    for item in range(n):
        top.append(sorted_list[item][0])

    return top

# returns a sorted list based on the euclidean distance
# takes a list of lists as an argument
def sort_by_distance(routes):
    ordered_values = []
    for path in routes:
        dist = fitness_score(path)
        if len(ordered_values) == 0:
            t = (path, dist)
            ordered_values.append(t)
        else:
            dist = fitness_score(path)
            placed = 0
            t = (path, dist)
            for j in range(len(ordered_values)):
                if ordered_values[j][1] > dist:
                    ordered_values.insert(j, t)
                    placed = 1
                    break
            if placed == 0:
                ordered_values.append(t)
    return ordered_values


# saves the supplied permutations to a file that can be used later
# for a better then random starting point
def save_state(routes, arg):
    f = open(arg, 'w')
    for line in routes:
        for item in line:
            f.write(str(item) + ' ')
        f.write('\n')
    f.close()


# shuffles the worst half (choosing lower half if equal ) of the top ten permutations 6 times then for 60 combos, keeps the 10 as is for total 70 and finally perform
# mutation by swapping 100 tiles around so that the tiles don't get locked in one half for 100 permutations from this generation
def worst_half_shuffle(best_parent, middle):
    children = []
    for parent in best_parent:
        top_score = fitness_score(parent, len(parent), middle)
        lower_score = fitness_score(parent, middle, 0)
        # shuffle worst half
        if top_score < lower_score:
            for j in range(9):
                temp = random_generation(0, middle, parent[:])
                assert (is_good_perm(temp))
                children.append(temp)
        else:
            for j in range(9):
                temp = random_generation(middle, len(parent), parent[:])
                children.append(temp)
        children.append(parent)
    return children


# shuffles a chunk of n cities randomly chosen given a particular starting point
# if a chunk of n length would exceed upper bounds subtracts n instead
def chunk_shuffle(best_parent, n):
    children = []
    for parent in best_parent:
        point = math.floor(random.random() * len(parent))
        if point + n > 999:
            t = random_generation(0, n, parent[point - n:point])
            temp = parent[:point - n] + t + parent[point:]
        else:
            t = random_generation(0, n, parent[point:point + n])
            temp = parent[:point] + t + parent[point + n:]
        assert (is_good_perm(temp))
        children.append(temp)
    children.append(parent)
    return children

# returns the average fitness score of a set of permutations
def avg_fitness(routes):
    n = len(routes)
    total = 0
    for route in routes:
        total += fitness_score(route)
    avg = total / n
    return avg


# reads in list of permutations from file to use as a as a starting point
def read_permutations(arg):
    try:
        file = open(arg)
    except OSError:
        print(f"Error: could not locate file \"{arg}\"")
    buf = []
    for line in file:
        buf.append(line.rstrip())
    p = []
    for entry in buf:
        entry_split = entry.split()
        perm = []
        for city in entry_split:
            perm.append(int(city))
        p.append(perm)

    return p

# oredered cross over randomly pairs a list of permutations then for each pair chooses two cut points the values between these cuts will remain unchanged
# the creates a sequence for each permutation starting at the second cut and wrapping to start  and finishing at point before second cut so every value is in
# the sequence then maps that sequence to the other permutation in the same order if a value exists between the cuts skips that value and moves on to the next value
def ox(choice):
    random.shuffle(choice)
    match = []
    size = len(choice[0])
    # length of half of the parents which is the amount of pairs to be assigned
    for y in range(int(len(choice) / 2)):
        match.append([choice[y * 2][:], choice[(y * 2 + 1)][:]])
    child_crossover = []
    for pair in match:
        cut_one = 0
        cut_two = 0

        while cut_one == 0 or cut_one == size - 1:
            cut_one = math.floor(random.random() * size)
        while cut_two == 0 or cut_two == size - 1 or cut_two == cut_one:
            cut_two = math.floor(random.random() * size)

        if cut_one > cut_two:
            cut_one, cut_two = cut_two, cut_one
        seq_one = pair[0][cut_two:] + pair[0][:cut_two]
        seq_two = pair[1][cut_two:] + pair[1][:cut_two]
        keep_one = pair[0][cut_one:cut_two]
        keep_two = pair[1][cut_one:cut_two]
        index = cut_two
        for x in seq_two:
            if x not in keep_one:
                pair[0][index] = x
                index += 1
            if index == size:
                index = 0
            if index == cut_one:
                break
        index = cut_two
        for g in seq_one:
            if g not in keep_two:
                pair[1][index] = g
                index += 1
            if index == size:
                index = 0
            if index == cut_one:
                break

        child_crossover.append(pair[0])
        child_crossover.append(pair[1])

    return child_crossover

#function taken from tsp.py in notes
def pmx(s, t):
    assert is_good_perm(s)
    assert is_good_perm(t)
    assert len(s) == len(t)
    n = len(s)

    # choose crossover point at random
    c = random.randrange(1, n - 1)  # c is index of last element of left part

    # first offspring
    first = s[:]
    i = 0
    while i <= c:
        j = first.index(t[i])
        first[i], first[j] = first[j], first[i]
        i += 1

    # second offspring
    second = t[:]
    i = 0
    while i <= c:
        j = second.index(s[i])
        second[i], second[j] = second[j], second[i]
        i += 1

    assert is_good_perm(first)
    assert is_good_perm(second)

    return first, second

#Helper function to run pmx several times from driver
def assemble_pmx(choice):
    random.shuffle(choice)
    match = []
    size = len(choice[0])
    # length of half of the parents which is the amount of pairs to be assigned
    for y in range(int(len(choice) / 2)):
        match.append([choice[y * 2][:], choice[(y * 2 + 1)][:]])
    child_crossover = []
    for pair in match:
        pair[0], pair[1] = pmx(pair[0], pair[1])
        child_crossover.append(pair[0])
        child_crossover.append(pair[1])
    return child_crossover

#taken from tsp.py in notes
def is_good_perm(lst):
    return sorted(lst) == list(range(1, len(lst) + 1))


# after n iterations will terminate and save
# newest generation to file will also terminate if the permutations selected are the same 10 times in a row
# runs a specific crossover function and mutate function on a set of permutations and there created children until
# n iterations
def driver(initial_routes, n, func=1, mutate=1):
    count = 0
    parents = selection(2, initial_routes)
    best = parents[0]
    while n > count:
        if func == 1:
            children = []
            temp = ox(parents[:])
            for t in temp:
                children.append(t)
        elif func == 2:
            children = []
            for j in range(5):
                temp = assemble_pmx(parents[0:2])
                for t in temp:
                    children.append(t)

        if mutate == 1:
            for item in range(len(children)):
                children[item] = random_mutation(children[item], 4)
        elif mutate == 2:
            children = worst_half_shuffle(children, 500)
        elif mutate == 3:
            children = chunk_shuffle(children, 30)
        elif mutate == 4:
            for item in range(len(children)):
                children[item] = random_mutation(children[item], 1)
                temp = random_mutation(children[item], 10)
                children.append(temp)
                temp = random_mutation(children[item], 25)
                children.append(temp)
                temp = chunk_shuffle([children[item][:]], 30)
                children.append(temp[0])
                temp = chunk_shuffle([children[item][:]], 60)
                children.append(temp[0])

        next_gen = selection(2, children)
        next_gen.append(best)

        count += 1
        parents = next_gen
        if fitness_score(parents[0]) < fitness_score(best):
            best = parents[0]
        print(fitness_score(best), count)
        for perm in next_gen:
            assert (is_good_perm(perm))

    save_state(next_gen, "permutations.txt")
    save_state([best], "best.txt")

#reads in two permutations sets then takes top n from each and combine into single set
def combine_permutation_set(arg1, arg2, n):
    p = read_permutations(arg1)
    t = read_permutations(arg2)
    p = selection(n, p)
    t = selection(n, t)
    s = t + p
    return s


if __name__ == '__main__':
    infobase = {}
    read_infobase("cities1000.txt")
    cross = None
    mutate_method = None
    gen = 1000

    #no permutation file given randomly generated instead
    if len(sys.argv) < 5:
        permutations = []
        for i in range(100):
            permutations.append(random_generation())
        if len(sys.argv) == 4:
            gen = int(sys.argv[1])
            cross = int(sys.argv[2])
            mutate_method = int(sys.argv[3])
        elif len(sys.argv) == 2:
            gen = int(sys.argv[1])
            cross = 1
            mutate_method = 1
        else:
            gen = 1000
            cross = 1
            mutate_method = 1
    #all arguments supplied
    else:
        gen = int(sys.argv[1])
        cross = int(sys.argv[2])
        mutate_method = int(sys.argv[3])
        if len(sys.argv) == 5:
            permutations = read_permutations(sys.argv[4])
        else:
            permutations = combine_permutation_set(sys.argv[4], sys.argv[5], 1)
    #records time of to solutions
    time_start = time.time()
    driver(permutations, gen, cross, mutate_method)
    time_total = time.time() - time_start
    print(time_total)


