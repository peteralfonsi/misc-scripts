# A simulation of the benchmark for spillover cache.
# Assumptions: the disk tier never fills, there are never collisions, the on-heap cache uses LRU (NOT lfu)
# We use positive numbers for repeated values and negative ones for non-repeated values.
# Values look like "-65.A", where the first part is the value, and the second part after "." is the "query type"

from collections import deque
import queue
import random
import hashlib

cache_size_kb = 40960 #81920 # 1 MB for larger scale test #5120
cheap_query_size_kb = 0.6 # each cheap query takes up 600 B
expensive_query_size_kb = 1.425

cheap_queries = ["A", "B", "C", "D", "E"]#, "X"]
expensive_queries = ["F", "G", "H", "I", "J", "K", "L", "M"]

cheap_time_ms = 10
medium_time_ms = 150 # will be 30 for some date histogram ones in current tests
expensive_time_ms = 150

def get_value_size(value):
    query_type = value.split(".")[-1]
    if query_type in expensive_queries:
        return expensive_query_size_kb
    elif query_type in cheap_queries:
        return cheap_query_size_kb
    raise Exception("Couldnt get value size")

# The cache is a deque. More frequently used items to the left, least frequent to the right.
class HeapTier:
    def __init__(self, max_size):
        self.deque = deque()
        self.set = set() # use set to quickly look up presence of items. Contains the same values as the deque
        self.size_internal = 0
        self.max_size = max_size

    def get_and_add(self, value, evict_max_one=False, evict_none=False):
        # Get the value, add it if not present
        # Returns [value found, list of evicted values]
        #try:
        if value in self.set:
            self.deque.remove(value)
            self.deque.appendleft(value) # append to left to mark as recently used
            self.set.add(value)
            return True, [] # true -> hit
        #except ValueError:
        else:
            # not in the deque - a miss. Add to queue
            self.size_internal += get_value_size(value)
            self.deque.appendleft(value)
            self.set.add(value)
            removed_list = []
            if evict_none: 
                return False, []
            while self.size_internal > self.max_size:
                removed = self.deque.pop()
                self.set.remove(removed)
                self.size_internal -= get_value_size(removed)
                removed_list.append(removed)
                if evict_max_one: 
                    break # for use in SLRU
                #print("Removed value, new size = {}".format(self.size))
            return False, removed_list

    def contains(self, value):
        # Check for presence of value, dont add it if not present
        return value in self.set

    def num_entries(self):
        return len(self.deque)

    def check_for_duplicates(self):
        value_set = set()
        num_duplicates = 0
        for value in self.deque:
            if value in value_set:
                num_duplicates += 1
            value_set.add(value)
        return num_duplicates
    
    def get_potential_victim(self): 
        if self.size_internal >= self.max_size: 
            return self.deque[-1] # rightmost entry? 
        return None
    
    def size(self): 
        return self.size_internal

class CaffeineHeapTier: 
    # Implement Window-TinyLFU to simulate a Caffeine cache 
    def __init__(self, max_size, reset_thresh, filter_k=100, doorkeeper_k=100): 
        self.max_size = max_size
        self.window_cache = HeapTier(max_size / 100) # window cache is a LRU cache 1% of the total cache size 
        self.tiny_lfu = TinyLfu(filter_k, doorkeeper_k, reset_thresh)
        self.main_cache = HeapTier(max_size * 99 / 100) # TODO: make this actually be an SLRU, for now just do normal LRU
        #self.main_cache = SLRU(max_size * 99 / 100, 0.2) # main cache is SLRU with 99% of total cache size. 80% of it is for hot items and 20% for cold (potential eviction) items

    def get_and_add(self, value):
        self.tiny_lfu.increment_frequency(value)
        was_in_window_cache, window_cache_evicted = self.window_cache.get_and_add(value) 
        if was_in_window_cache: 
            return True, []
        was_in_main_cache = self.main_cache.contains(value)
        all_evicted = []
        # Problem: Window cache may evict multiple? In this case, i guess we iterate thru the window cache evictions
        for w_victim in window_cache_evicted: 
            main_victim = self.main_cache.get_potential_victim() 
            # What if w_victim is large and would require multiple potential main cache victims?
            # It seems like caffeine ignores this
            victim = self.tiny_lfu.pick_victim(w_victim, main_victim)
            if victim is w_victim: 
                pass # nothing happens, as window cache has already evicted it. But count evictions? 
            elif victim is main_victim: 
                #self.main_cache.evict(main_victim) 
                evict_none = victim is None
                _, main_evicted = self.main_cache.get_and_add(w_victim, evict_max_one=True, evict_none=evict_none) # the add() call should not cause any addtl evictions since caffeine only evicts one - implement SLRU this way
                if victim is not None:
                    assert len(main_evicted) <= 1 # ok so often this has length 0 which we dont expect...
                    if len(main_evicted) > 0:
                        assert main_evicted[0] == main_victim
                    #print("check!")
                else: 
                    assert len(main_evicted) == 0
            all_evicted.append(victim)
        return was_in_main_cache, all_evicted
            
    def contains(self, value): 
        return self.window_cache.contains(value) or self.main_cache.contains(value)

    def num_entries(self): 
        return self.window_cache.num_entries() + self.main_cache.num_entries()
    
    def size(self): 
        return self.window_cache.size() + self.main_cache.size()
    
class TinyLfu: 
    # https://arxiv.org/pdf/1512.00727
    def __init__(self, filter_k, doorkeeper_k, reset_thresh): 
        # TODO 
        # reset_thresh should be W / C (although it's not clear to me what W really is)
        self.cbf = MinimalIncrementCBF(filter_k)
        self.doorkeeper = Doorkeeper(doorkeeper_k)
        self.reset_thresh = reset_thresh
        self.increment_counter = 0

    def increment_frequency(self, item): 
        # I think we call this any time this enters the cache at all, including window cache, 
        # otherwise we can't estimate frequency for window victims
        if not self.doorkeeper.contains(item): 
            self.doorkeeper.add(item)
        else: 
            self.cbf.add(item)
            self.increment_counter += 1 
            if self.increment_counter >= self.reset_thresh: 
                self.doorkeeper.reset() 
                self.cbf.reset()
                self.increment_counter = 0

    def estimate_frequency(self, item): 
        is_in_doorkeeper = self.doorkeeper.contains(item) 
        estimate = self.cbf.estimate(item)
        if is_in_doorkeeper: 
            estimate += 1 
        return estimate

    def pick_victim(self, window_victim, main_victim): 
        if main_victim == None: 
            return None
        window_victim_freq = self.estimate_frequency(window_victim) 
        main_victim_freq = self.estimate_frequency(main_victim) 
        if window_victim_freq <= main_victim_freq: 
            return window_victim
        return main_victim

def hash(item, i, k): 
        # get the i-th hash function of the item by hashing str(i) + str(item) with sha256
        hash_obj = hashlib.sha256()
        hash_obj.update(i.to_bytes(4, byteorder="big"))
        hash_obj.update(item.encode()) 
        return int(hash_obj.hexdigest(), 16) % k

class Doorkeeper: 
    # Just a normal bloom filter
    def __init__(self, k): 
        self.k = k
        self.filter = []
        for i in range(k): 
            self.filter.append(False)

    def add(self, item): 
        for i in range(self.k): 
            self.filter[hash(item, i, self.k)] = True 
    
    def contains(self, item): 
        for i in range(self.k): 
            if not self.filter[hash(item, i, self.k)]: 
                return False 
        return True
    
    def reset(self): 
        for i in range(self.k): 
            self.filter[i] = False

class MinimalIncrementCBF: 
    def __init__(self, k): 
        self.k = k # number of entries in bloom filter
        self.filter = [] 
        for i in range(k): 
            self.filter.append(0)
    
    def estimate(self, item): 
        bloom_indices_and_values = set()
        for i in range(self.k): 
            bloom_index = hash(item, i, self.k)
            bloom_indices_and_values.add((bloom_index, self.filter[bloom_index]))
        min_filter_value = min(bloom_indices_and_values, key=lambda x: x[1])[1] # get the minimum value for values this key maps to in the filter
        return min_filter_value
    
    def add(self, item): 
        bloom_indices_and_values = set()
        for i in range(self.k): 
            bloom_index = hash(item, i, self.k)
            bloom_indices_and_values.add((bloom_index, self.filter[bloom_index]))
        min_filter_value = min(bloom_indices_and_values, key=lambda x: x[1])[1]
        for pair in bloom_indices_and_values: 
            # increment only the minimal values
            if pair[1] == min_filter_value: 
                self.filter[pair[0]] += 1

    def reset(self): 
        # divide all values by 2 (integer div) 
        for i in range(self.k): 
            self.filter[i] = self.filter[i] // 2


class SLRU: 
    def __init__(self): 
        self.base_hash = hashlib.sha256()
        pass
    


class DiskTier:
    def __init__(self, H=1, X=None, uses_promotion=False, promotes_in_batches=False, batch_size=100):
        self.set = set()
        self.H = H
        self.X = X
        self.uses_promotion = uses_promotion
        self.promotes_in_batches = promotes_in_batches
        self.batch_size = batch_size

        self.last_hits_queue = queue.Queue(maxsize=self.H)
        self.last_hits_frequency_dict = {}

        self.ready_to_promote = []
        self.size_internal = 0


    def get(self, value):
        # Get the value, but don't add it if not present
        # returns (whether the value was found, list of values that need to be promoted to the heap tier)
        if value in self.set:
            promoted_values = []
            if self.uses_promotion:
                self.last_hits_queue.put(value)
                if value in self.last_hits_frequency_dict:
                    self.last_hits_frequency_dict[value] += 1
                else:
                    self.last_hits_frequency_dict[value] = 1
                if self.last_hits_queue.full():
                    Hth_most_recent_hit = self.last_hits_queue.get()
                    if Hth_most_recent_hit in self.set:
                        if self.last_hits_frequency_dict[Hth_most_recent_hit] <= 1:
                            self.last_hits_frequency_dict[Hth_most_recent_hit] = 0 #.pop(Hth_most_recent_hit, None)
                        else:
                            self.last_hits_frequency_dict[Hth_most_recent_hit] -= 1

                if not self.promotes_in_batches:
                    if self.last_hits_frequency_dict[value] >= self.X:
                        promoted_values.append(value)

                    for pv in promoted_values:
                        self.remove(pv)

                else:
                    promoted_values = [] # dont actually promote anything yet, unless batch size is reached
                    if self.last_hits_frequency_dict[value] >= self.X and value not in self.ready_to_promote:
                        self.ready_to_promote.append(value)
                        #print("{} ready to promote".format(len(self.ready_to_promote)))
                    if len(self.ready_to_promote) >= self.batch_size:
                        promoted_values += self.ready_to_promote.copy()
                        for pv in self.ready_to_promote:
                            #print("Removed {} via batch promotion".format(pv))
                            self.remove(pv)
                        self.ready_to_promote = []


            return True, promoted_values
        else:
            return False, []

    def add(self, value):
        self.set.add(value)
        self.size_internal += get_value_size(value)

    def remove(self, value):
        self.set.remove(value)
        self.size_internal -= get_value_size(value)
        if value in self.last_hits_frequency_dict:
            #self.last_hits_frequency_dict.pop(value, None)
            self.last_hits_frequency_dict[value] = 0
        # issue: not easy to remove it from the queue...
        # to get around this, check for presence in set when getting from queue (not scalable)

    def num_entries(self):
        return len(self.set)
    
    def size(self): 
        return self.size_internal

class SpilloverStats:
    def __init__(self):
        self.heap_misses = 0
        self.heap_hits = 0
        self.disk_misses = 0
        self.disk_hits = 0
        self.promotions = 0

    def print(self, has_disk_tier=True):
        print("Heap hits = {}".format(self.heap_hits))
        print("Heap misses = {}".format(self.heap_misses))
        if has_disk_tier:
            print("Disk hits = {}".format(self.disk_hits))
            print("Disk misses = {}".format(self.disk_misses))
            print("Total hit rate = {}".format((self.heap_hits + self.disk_hits) / (self.heap_hits + self.disk_hits + self.disk_misses)))
            print("{:.2f}% of hits are from heap tier".format(self.heap_hits / (self.heap_hits + self.disk_hits) * 100))
            print("{} promotions back to heap tier".format(self.promotions))
        else:
            print("Total hit rate = {}".format(self.heap_hits / (self.heap_hits + self.heap_misses)))

    #def write_state_to_csv(self)

def get_value(rf, repeat_supplier, query_type):
    if query_type == "X":
        # try to replicate the passengers query which has very few permutations
        return str(random.randint(1, 16)) + "." + query_type

    if random.random() < rf:
        value = repeat_supplier()
    else:
        value = -1 * random.randint(1, 1000000000)

    ret = str(value) + "." + query_type
    #print(ret)
    return ret


def get_spillover(value, heap_tier, disk_tier, approximate_policy=False):
    # returns "heap" or "disk" if hits on those, otherwise returns None
    # was_heap_hit, evicted = heap_tier.get(value)

    # check for presence without adding it if it's not there
    is_in_heap = heap_tier.contains(value)
    if is_in_heap:
        # now actually get it (triggering evictions possibly)
        _, evicted = heap_tier.get_and_add(value)
        for evicted_value in evicted:
            # Attempting to simulate effects of 10 ms policy where cheap queries basically never reach disk tier
            query_type = evicted_value.split(".")[-1]
            if query_type in expensive_queries or not approximate_policy:
                disk_tier.add(evicted_value)
        return "heap", evicted
    else:
        # check if it's in the disk tier. If not, its a miss everywhere, and add it to the heap tier
        is_in_disk, _ = disk_tier.get(value)
        if is_in_disk:
            return "disk", []
        else:
            _, evicted = heap_tier.get_and_add(value)
            for evicted_value in evicted:
                # Attempting to simulate effects of 10 ms policy where cheap queries basically never reach disk tier
                query_type = evicted_value.split(".")[-1]
                if query_type in expensive_queries or not approximate_policy:
                    disk_tier.add(evicted_value)
            return None, evicted

def get_spillover_with_promotion(value, heap_tier, disk_tier):
    # returns "heap" or "disk" if hits on those, otherwise returns None
    # also returns evicted values, number of promoted values
    # was_heap_hit, evicted = heap_tier.get(value)

    # check for presence without adding it if it's not there
    is_in_heap = heap_tier.contains(value)
    if is_in_heap:
        # now actually get it (triggering evictions possibly)
        _, evicted = heap_tier.get_and_add(value)
        for evicted_value in evicted:
            disk_tier.add(evicted_value)
        return "heap", evicted, 0
    else:
        # check if it's in the disk tier. If not, its a miss everywhere, and add it to the heap tier
        is_in_disk, promoted_values = disk_tier.get(value)
        evicted = []

        prom_evicted_count = 0
        for pv in promoted_values:
            _, promoted_evicted = heap_tier.get_and_add(pv)
            prom_evicted_count += len(promoted_evicted)
            evicted += promoted_evicted
        #if prom_evicted_count > 0:
            #print("# evicted from promotions = {}".format(prom_evicted_count))
        for evicted_value in evicted:
            disk_tier.add(evicted_value)

        if not is_in_disk:
            _, evicted_from_new_key = heap_tier.get_and_add(value)
            for evicted_value in evicted_from_new_key:
                disk_tier.add(evicted_value)
            evicted += evicted_from_new_key
            return None, evicted, len(promoted_values)
        else:
            return "disk", [], len(promoted_values)


def get_main(value, heap_tier):
    was_heap_hit, evicted = heap_tier.get_and_add(value)
    if was_heap_hit:
        return "heap", evicted
    return None, evicted

def update_stats(result, stats, has_disk_tier=True):
    if result is None:
        stats.heap_misses += 1
        if has_disk_tier:
            stats.disk_misses += 1
    elif result == "disk":
        stats.heap_misses += 1
        if has_disk_tier:
            stats.disk_hits += 1
    elif result == "heap":
        stats.heap_hits += 1


def test_spillover_cache(rf, repeat_supplier, num_iter_cheap, num_iter_expensive, use_promotion=False, uses_batching=False, use_caffeine=False, approximate_policy=False):
    heap_tier = HeapTier(cache_size_kb)
    if use_caffeine: 
        # estimate W / C as ?? If W is meant to be the universe size, roughly 
        reset_thresh = (num_iter_cheap * cheap_query_size_kb + num_iter_expensive * expensive_query_size_kb) / cache_size_kb
        heap_tier = CaffeineHeapTier(cache_size_kb, reset_thresh, filter_k = 100, doorkeeper_k = 100)
    disk_tier = DiskTier()
    if use_promotion:
        if uses_batching:
            disk_tier = DiskTier(uses_promotion=True, H=500, X=2, promotes_in_batches=True, batch_size=100)
        else:
            disk_tier = DiskTier(uses_promotion=True, H=500, X=2)
    stats = SpilloverStats()

    # keep track of how many times things were hits on disk -
    # Sagar's theory would require at least 3 (spills to disk, hit on disk, which would otherwise have pulled back into heap, then another hit)

    disk_hit_freq_map = {} # debug only
    cheap_mult = int(num_iter_cheap / num_iter_expensive) # should be an int before rounding
    for i in range(num_iter_expensive):
        iter_values = []
        for cheap_query_type in cheap_queries:
            for j in range(cheap_mult):
                iter_values.append(get_value(rf, repeat_supplier, cheap_query_type))
        for expensive_query_type in expensive_queries:
            iter_values.append(get_value(rf, repeat_supplier, expensive_query_type))

        random.shuffle(iter_values)
        for value in iter_values:
            if use_promotion:
                result, evicted, num_promoted = get_spillover_with_promotion(value, heap_tier, disk_tier)
                stats.promotions += num_promoted
            else:
                result, evicted = get_spillover(value, heap_tier, disk_tier, approximate_policy=approximate_policy)
            '''if result == "disk":
                if value in disk_hit_freq_map:
                    disk_hit_freq_map[value] += 1
                else:
                    disk_hit_freq_map[value] = 1'''

            update_stats(result, stats)
        if i % 1000 == 0:
            print("Done with iter {}/{}".format(i, num_iter_expensive))
            print("Heap size = {} MB, disk size = {} MB, disk entries = {}, heap hits = {}, disk hits = {}, heap hit fraction = {}%".format(heap_tier.size() / 1024, disk_tier.size() / 1024, disk_tier.num_entries(), stats.heap_hits, stats.disk_hits, 100 * stats.heap_hits / (stats.heap_hits + stats.disk_hits)))
            #print("Found {} duplicates in heap tier".format(heap_tier.check_for_duplicates()))
    '''num_exceeding = [0, 0, 0, 0, 0]
    num_exceeding_keys = []
    for i in range(len(num_exceeding)):
        num_exceeding_keys.append([])

    for key, value in disk_hit_freq_map.items():
        for num_hits in range(1, len(num_exceeding)):
            if value > num_hits:
                num_exceeding[num_hits] += 1
                num_exceeding_keys[num_hits].append(key)'''
    '''for i in range(1, len(num_exceeding)):
        print("{} keys accessed > {} times from disk".format(num_exceeding[i], i))
        print("Number of keys called >2 times from disk:")
        print(num_exceeding_keys[2])'''
    return stats, heap_tier.num_entries(), disk_tier.num_entries(), None





def test_main_cache(rf, repeat_supplier, num_iter_cheap, num_iter_expensive):
    heap_tier = HeapTier(cache_size_kb)
    stats = SpilloverStats()

    cheap_mult = int(num_iter_cheap / num_iter_expensive) # should be an int before rounding
    evicted_list = []
    for i in range(num_iter_expensive):
        iter_values = []
        for cheap_query_type in cheap_queries:
            for j in range(cheap_mult):
                iter_values.append(get_value(rf, repeat_supplier, cheap_query_type))
        for expensive_query_type in expensive_queries:
            iter_values.append(get_value(rf, repeat_supplier, expensive_query_type))
        random.shuffle(iter_values)
        for value in iter_values:
            result, evicted = get_main(value, heap_tier)
            update_stats(result, stats, has_disk_tier=False)
            evicted_list += evicted
        if i % 1000 == 0:
            print("Done with iter {}/{}".format(i, num_iter_expensive))
    return stats, heap_tier.num_entries(), evicted_list



# Zipf-related stuff below

def H(i, H_list):
    # compute the harmonic number H_n,m = sum over i from 1 to n of (1 / i^m)
    return H_list[i-1] #sum([1 / (i ** m) for i in range(1, n+1)])

def precompute_H(n, m):
    H_list = [1]
    for j in range(2, n+1):
        #H_list.append(sum([1 / (i ** m) for i in range(1, j+1)]))
        H_list.append(H_list[-1] + 1 / (j ** m))
    return H_list

def zipf_cdf_inverse(u, H_list):
    # To map a uniformly distributed u from [0, 1] to some probability distribution we plug it into its inverse CDF.
    # as the zipf cdf is discontinuous there is no real inverse but we can use this solution:
    # https://math.stackexchange.com/questions/53671/how-to-calculate-the-inverse-cdf-for-the-zipf-distribution
    # Precompute all values H_i,alpha for a fixed alpha and pass in as H_list
    if (u < 0 or u >= 1):
        raise Exception("Input u must have 0 <= u < 1")
    n = len(H_list)
    candidate_return = 1
    denominator = H(n, H_list)
    numerator = 0
    while candidate_return < n:
        numerator = H(candidate_return, H_list)
        #print(u, candidate_return, numerator, denominator, numerator/denominator)
        if u < numerator / denominator:
            return candidate_return
        candidate_return += 1
    return n

zipf_N = 10000 #5000 #50000 #10000 # 5000
zipf_alpha = 0.9 #0.9 #1
H_list = precompute_H(zipf_N, zipf_alpha)
print("Done precomputing H values")

def zipf_repeat_supplier():
    u = random.random()
    return zipf_cdf_inverse(u, H_list)

# Actually test zipf spillover cache

cheap_mult = 4
num_iter = 1000000 #10000 #150000 #30000 #400000
rf = 0.7 #0.65 #1 #0.5
seed = 44 #random.randint(1, 100)

'''print("TESTING SPILLOVER CACHE WITH CAFFEINE")
random.seed(seed)
stats, heap_entries, disk_entries, disk_tier_contents = test_spillover_cache(rf, zipf_repeat_supplier, cheap_mult*num_iter, num_iter, use_caffeine=True)
stats.print()
print("{} heap entries".format(heap_entries))
print("{} disk entries".format(disk_entries))'''

print("TESTING SPILLOVER CACHE")
random.seed(seed)
stats, heap_entries, disk_entries, disk_tier_contents = test_spillover_cache(rf, zipf_repeat_supplier, cheap_mult*num_iter, num_iter, approximate_policy=False)
stats.print()
print("{} heap entries".format(heap_entries))
print("{} disk entries".format(disk_entries))

print("TESTING MAIN CACHE")
random.seed(seed)
main_stats, main_heap_entries, evicted_list = test_main_cache(rf, zipf_repeat_supplier, cheap_mult*num_iter, num_iter)
main_stats.print(has_disk_tier=False)

print("TESTING SPILLOVER CACHE WITH PROMOTION")
random.seed(seed)
stats, heap_entries, disk_entries, disk_tier_contents = test_spillover_cache(rf, zipf_repeat_supplier, cheap_mult*num_iter, num_iter, use_promotion=True)
stats.print()
print("{} heap entries".format(heap_entries))
print("{} disk entries".format(disk_entries))

print("TESTING SPILLOVER CACHE WITH PROMOTION AND BATCH SIZE")
random.seed(seed)
stats, heap_entries, disk_entries, disk_tier_contents = test_spillover_cache(rf, zipf_repeat_supplier, cheap_mult*num_iter, num_iter, use_promotion=True, uses_batching=True)
stats.print()
print("{} heap entries".format(heap_entries))
print("{} disk entries".format(disk_entries))


#print("{} heap entries".format(main_heap_entries))

#print("Evicted list in main exactly matches disk tier contents: ", sorted(disk_tier_contents) == sorted(evicted_list))

