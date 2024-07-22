import matplotlib.pyplot as plt

runs = ["HHC5", "HHC6", "HHC7", "HHC8"]
#["S1", "S2", "S3", "S4", "S5", "S6"]

run_label_map = {
    "HC5":"HC1",
    "HC6":"HC2",
    "HC7":"HC3",
    "HC8":"HC4",
}

def get_rss_gb(run_name): 
    fp = "memory_usages/mem_{}.txt".format(run_name)
    rss_values = []
    with open(fp, "r") as f: 
        for line in f: 
            rss_values.append(int(line.split(" ")[-1]) / (1024 * 1024))
    return rss_values

def compare_all(): 
    for run in runs: 
        rss_values = get_rss_gb(run)
        plt.plot(range(len(rss_values)), rss_values, label=run_label_map.get(run, run))
    plt.legend()
    plt.xlabel("Timestep (min)")
    plt.ylabel("Memory used (GB)")
    plt.grid(True)
    plt.title("Memory used (GB) over time per run")
    plt.show()

compare_all()

