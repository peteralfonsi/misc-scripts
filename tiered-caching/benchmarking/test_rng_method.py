import random 
from queue import Queue

num_iter = 3000
frac = 0.8
flat_max = 200
sub_buffer = 35

def get_mb(repeats): 
    return "{:.3f} MB".format(15 * repeats / 1000)

def format_output(tup): 
    return "Observed counter max = {}, observed hit rate = {:.3f}, repeated volume = {}".format(tup[0], tup[1], tup[2])

def get_true_repeat_percentage_frac(repeat_freq): 
    counter_max = 0
    repeats = []
    total_repeats = 0
    for j in range(num_iter): 
        repeats.append(0)
    for i in range(num_iter): 
        if random.random() < repeat_freq: 
            i = random.randrange(0, counter_max + 1)
            if i > frac * counter_max - 1: 
                counter_max += 1
            if repeats[i] > 0: 
                total_repeats += 1
            repeats[i] += 1 
    distinct_repeats = 0
    for j in range(num_iter): 
        if repeats[j] > 1: 
            distinct_repeats += 1
    return (counter_max, total_repeats / num_iter, get_mb(distinct_repeats))

def get_true_repeat_percentage_flat(repeat_freq, flat_max=500): 
    repeats = [] 
    total_repeats = 0
    for j in range(num_iter): 
        repeats.append(0)
    for i in range(num_iter): 
        if random.random() < repeat_freq: 
            i = random.randrange(0, flat_max)
            if repeats[i] > 0: 
                total_repeats += 1
            repeats[i] += 1 
    distinct_repeats = 0
    for j in range(num_iter): 
        if repeats[j] > 1: 
            distinct_repeats += 1
    return (flat_max, total_repeats / num_iter, get_mb(distinct_repeats))

def get_true_repeat_percentage_current(repeat_freq): 
    counter_max = 0
    repeats = [] 
    total_repeats = 0
    for j in range(num_iter): 
        repeats.append(0)
    for i in range(num_iter): 
        if random.random() < repeat_freq: 
            i = random.randrange(0, counter_max + 1)
            if i == counter_max: 
                counter_max += 1
            if repeats[i] > 0: 
                total_repeats += 1
            repeats[i] += 1 
    distinct_repeats = 0
    for j in range(num_iter): 
        if repeats[j] > 0: 
            distinct_repeats += 1
    return (counter_max, total_repeats / num_iter, get_mb(distinct_repeats))

def get_true_repeat_percentage_sub_buffer(repeat_freq, buffer=10): 
    counter_max = 0
    repeats = []
    total_repeats = 0
    for j in range(num_iter): 
        repeats.append(0)
    for i in range(num_iter): 
        if random.random() < repeat_freq: 
            i = random.randrange(0, counter_max + 1)
            if i > counter_max - buffer: 
                counter_max += 1
            if repeats[i] > 0: 
                total_repeats += 1
            repeats[i] += 1 
    distinct_repeats = 0
    for j in range(num_iter): 
        if repeats[j] > 1: 
            distinct_repeats += 1
    return (counter_max, total_repeats / num_iter, get_mb(distinct_repeats))

def two_lists(repeat_freq): 
    all_value_len = 10000
    all_value_list = []
    for j in range(all_value_len): 
        all_value_list.append([j, 0]) # value, # uses
    random.shuffle(all_value_list) 

    main_list = Queue()
    second_list = Queue()
    for pair in all_value_list: 
        main_list.put(pair)

    repeats = []
    total_repeats = 0
    for j in range(all_value_len): 
        repeats.append(0)
    for i in range(num_iter): 
        if random.random() < repeat_freq: 
            if second_list.empty(): 
                pair = main_list.get() 
            else: 
                pair = second_list.get() 
            i = pair[0] 
            if repeats[i] > 0: 
                total_repeats += 1
            repeats[i] += 1 
            pair[1] += 1 # inc number of times this has been used
            if pair[1] == 1: 
                second_list.put(pair)
    distinct_repeats = 0
    for j in range(all_value_len): 
        if repeats[j] > 1: 
            distinct_repeats += 1
    return (0, total_repeats / num_iter, get_mb(distinct_repeats))

for rf in [0, 0.1, 0.3, 0.65]: 
    print("RF = {}".format(rf))
    print("NEW")
    print(format_output(get_true_repeat_percentage_frac(rf)))
    print("CURRENT")
    print(format_output(get_true_repeat_percentage_current(rf)))
    print("FLAT {}".format(flat_max))
    print(format_output(get_true_repeat_percentage_flat(rf, flat_max=flat_max)))
    print("BUFFER {}".format(sub_buffer))
    print(format_output(get_true_repeat_percentage_sub_buffer(rf, buffer=sub_buffer)))
    print("TWO LISTS")
    print(format_output(two_lists(rf)))
    print("")