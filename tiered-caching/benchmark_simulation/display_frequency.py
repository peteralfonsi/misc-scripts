import matplotlib.pyplot as plt
import csv

to_display = "2024_09_18_14_26.csv" # rf=30%, 500k iter run, no promo
#"2024_09_16_18_48.csv" # 30%, 80k iter, promo = 5, alpha = 0.7
#"2024_09_16_18_44.csv" # 30%, 80k iter, no promo, alpha = 0.7
#"2024_09_16_18_40.csv" # 30%, 300k iter, no promo, alpha = 1.5
#"2024_09_16_18_38.csv" # 30%, 80k iter, no promo, alpha = 1.5
#"2024_09_16_18_14.csv" # 30%, 300k iter, promo = 5
#"2024_09_16_18_06.csv" # 30%, 80k iter, promo = 3
#"2024_09_16_18_04.csv" # 30%, 80k iter run, with promo threshold = 20
#"2024_09_16_18_00.csv" # 30%, 80k iter run, with promo threshold = 10
#"2024_09_16_17_48.csv" # 30%, 80k iter run, with promo threshold = 1
#"2024_09_16_16_02.csv" # 30%, 80k iter run, with promotion threshold = 5
#"2024_09_16_15_27.csv" # 70%, 300k iter run
#"2024_09_16_14_42.csv" # rf = 30%, 300k iter run
#"2024_09_16_13_30.csv" # initial rf=30%, 80k iter run
zipf_N = 10_000 # must match the value used when generating the file

cheap_queries = ["A", "B", "C", "D", "E"]
expensive_queries = ["F", "G", "H", "I", "J", "K", "L", "M"]

freqs = {}
fp = "frequency_maps/{}".format(to_display)
with open(fp, "r") as f: 
    reader = csv.reader(f)
    next(reader, None) # skip header
    freqs = {rows[0]:(int(rows[1]), int(rows[2])) for rows in reader} # create dict from value column -> (heap hits, disk hits)

def get_value(letter, i): 
    return str(i) + "." + letter

cheap_heap_averages = []
expensive_heap_averages = []
cheap_disk_averages = []
expensive_disk_averages = []
for queries, heap_result, disk_result in zip([cheap_queries, expensive_queries], [cheap_heap_averages, expensive_heap_averages], [cheap_disk_averages, expensive_disk_averages]):
    for i in range(1, zipf_N): 
        heap_tot = 0
        disk_tot = 0
        for letter in queries: 
            heap_tot += freqs[get_value(letter, i)][0]
            disk_tot += freqs[get_value(letter, i)][1]
        heap_result.append(heap_tot / len(queries))
        disk_result.append(disk_tot / len(queries))

heap_color = "tomato"
disk_color = "skyblue"

def raw_freq_graph():
    fig, ax = plt.subplots(nrows=1, ncols=2) 
    i = 0
    for heap_averages, disk_averages, title in zip([expensive_heap_averages, cheap_heap_averages], [expensive_disk_averages, cheap_disk_averages], ["expensive", "cheap"]):
        heap_averages_sum = sum(heap_averages)
        heap_hit_rate_fraction = heap_averages_sum / (sum(disk_averages) + heap_averages_sum)
        x = range(1, zipf_N)
        ax[i].bar(x, heap_averages, color=heap_color, width=1.0, align="edge")
        ax[i].bar(x, disk_averages, bottom=heap_averages, color=disk_color, width=1.0, align="edge")
        ax[i].grid(True)
        ax[i].set_xscale("log")
        ax[i].set_yscale("log")
        ax[i].set_ylabel("Average hit frequency")
        ax[i].set_xlabel("Zipf frequency index")
        ax[i].set_title("Disk and heap hit frequency for {} queries".format(title))
        ax[i].text(0.95, 0.95, "Heap hit rate fraction = {:.3f}".format(heap_hit_rate_fraction), transform=ax[i].transAxes, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), verticalalignment='top', horizontalalignment='right')
        i += 1
    plt.show()

def ratio_graph(): 
    # this graph is "equal-area" aka the area that is orange on the graph is proportional to the fraction of hits that come from heap
    # (approximately as there is a bit of noise and the hit values aren't exactly along the zipfian line in log-log space but its close in practice)
    fig, ax = plt.subplots(nrows=1, ncols=2) 
    i = 0
    for heap_averages, disk_averages, title in zip([expensive_heap_averages, cheap_heap_averages], [expensive_disk_averages, cheap_disk_averages], ["expensive", "cheap"]):
        heap_averages_sum = sum(heap_averages)
        heap_hit_rate_fraction = heap_averages_sum / (sum(disk_averages) + heap_averages_sum)
        heap_fractions = []
        disk_fractions = []
        for h, d in zip(heap_averages, disk_averages): 
            tot = h + d
            if tot == 0: 
                heap_fractions.append(0)
                disk_fractions.append(0)
            else: 
                heap_fractions.append(h / tot)
                disk_fractions.append(d / tot)
        x = range(1, zipf_N)
        ax[i].bar(x, heap_fractions, color=heap_color, width=1.0, align="edge")
        ax[i].bar(x, disk_fractions, bottom=heap_fractions, color=disk_color, width=1.0, align="edge")
        ax[i].grid(True)
        ax[i].set_xscale("log")
        ax[i].set_ylabel("Fraction of hits from heap tier")
        ax[i].set_xlabel("Zipf frequency index")
        ax[i].set_title("Disk and heap hit frequency for {} queries".format(title))
        ax[i].text(0.95, 0.95, "Heap hit rate fraction = {:.3f}".format(heap_hit_rate_fraction), transform=ax[i].transAxes, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), verticalalignment='top', horizontalalignment='right')
        i += 1
    plt.show()

ratio_graph()
#raw_freq_graph()