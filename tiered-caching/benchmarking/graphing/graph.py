import matplotlib.pyplot as plt 
import pandas as pd 
import numpy as np

plt.rcParams['font.size'] = 9

# run to_csv.py to refresh this file if new results are added
df = pd.read_csv("all_results.csv") 

y_values = [
    "Min Throughput",
    "Median Throughput", 
    "50th percentile latency", 
    "90th percentile latency", 
    "99th percentile latency", 
    "100th percentile latency"
]
# Make a grouped bar chart, where the group is the task, the different entries in the groups are the runs, 
# and the y axis is the entry in y_values 
query_groups = list(df[df["Run"] == "tiered_00"]["Operation"].unique())
try: 
    query_groups.remove("date_histogram_fixed_interval_with_metrics")
    query_groups.remove("auto_date_histogram_with_metrics") # These ones don't seem to work, even though they come with nyc_taxis
except ValueError: 
    pass
# Don't graph the randomized-only ones for now 
to_remove = []
'''for item in query_groups: 
    if item.startswith("cheap-"):
        to_remove.append(item)'''
for item in to_remove: 
    try:
        query_groups.remove(item)
    except ValueError: 
        pass
query_groups = tuple(query_groups)
print(query_groups)

runs_to_display = [
    "tiered_00",
    "tiered_01",
    "tiered_03",
    "tiered_065",
    "disk_off_00",
    "disk_off_01",
    "disk_off_03",
    "disk_off_065",
    "main_00",
    "main_01",
    "main_03",
    "main_065",
]

'''"tiered_jar_disk_off_rf00", 
    "tiered_jar_disk_off_rf01", 
    "tiered_jar_disk_off_rf03", 
    "tiered_jar_disk_off_rf065", 
    "tiered_jar_disk_on_rf00", 
    "tiered_jar_disk_on_rf01", 
    "tiered_jar_disk_on_rf03", 
    "tiered_jar_disk_on_rf065",'''

run_types = ["tiered", "disk_off", "main"]
percentages = ["00", "01", "03", "065"]
pct_label_map = {"00":"0%", "01":"10%", "03":"30%", "065":"65%"}

legend_names = {
    
}
for run in runs_to_display: 
    legend_names[run] = run

# based on https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html
def do_standard(): 
    for value in y_values: 
        run_values = {}
        val_df = df[df["Task"] == value]
        unit = val_df["Unit"].unique()[0]
        for run in runs_to_display: 
            run_df = val_df[val_df["Run"] == run]
            print(run)
            run_values[run] = tuple([run_df[run_df["Operation"] == op]["Time"].iloc[0] for op in query_groups])

        x = np.arange(len(query_groups))
        width = 0.05
        multiplier = 0
        print(run_values)

        fig, ax = plt.subplots(layout="constrained") 
        for run_title, time in run_values.items(): 
            offset = width * multiplier 
            print(run_title, time)
            rects = ax.barh(x + offset, time, width, label=legend_names[run_title]) 
            ax.bar_label(rects, padding=3, fmt="%.1f") # fmt="%.2e", rotation=90
            multiplier += 1
        
        ax.set_title("{} by query type".format(value), y=1.08)
        ax.set_yticks(x+width, query_groups)
        if unit == "ms": 
            ax.set_xscale("log")
            ax.set_xlabel("{} ({}, log)".format(value, unit))
        else: 
            ax.set_xlabel("{} ({})".format(value, unit))
        ax.legend()
        ax.grid(True)
        plt.show()

def get_descriptor(kind, percentage): 
    return "{}, rf = {}".format(kind, pct_label_map[percentage])

def do_percentage(averages=False): 
    # plot percentage scatter plot 
    fig, ax = plt.subplots(layout="constrained") 
    # insert empty one in between each query type to space out groups?
    for value in y_values: 
        run_values = {}
        val_df = df[df["Task"] == value] # throughput, latency, etc
        unit = val_df["Unit"].unique()[0]
        
        x = []
        y_tiered = []
        y_disk_off = [] 

        x_avg = [] # for average of all expensive queries 0%, 10%, ... 
        rolling_percentage_sums = {} # contains rolling sum of percentages for each category (ex: cheap queries with 65% rf)
        for kind in ["Cheap", "Expensive"]: 
            for p in percentages: 
                rolling_percentage_sums[get_descriptor(kind, p)] = [0, 0] # tiered sum, disk off sum
                

        num_expensive = 0
        num_cheap = 0
        for i, query_type in enumerate(query_groups): 
            if "cheap" in query_type: 
                num_cheap += 1 
                kind = "Cheap"
            else: 
                num_expensive += 1
                kind = "Expensive"

            q_df = val_df[val_df["Operation"] == query_type]
            for rf in percentages: 
                rf_df = q_df[q_df["Percentage"] == rf]
                print(rf_df)
                tiered_time = rf_df[rf_df["Run type"] == "tiered"]["Time"].iloc[0]
                disk_off_time = rf_df[rf_df["Run type"] == "disk_off"]["Time"].iloc[0]
                main_time = rf_df[rf_df["Run type"] == "main"]["Time"].iloc[0]
                x.append("{}, rf = {}".format(query_type, rf))
                y_tiered.append(tiered_time / main_time * 100)
                y_disk_off.append(disk_off_time / main_time * 100)
                rolling_percentage_sums[get_descriptor(kind, rf)][0] += y_tiered[-1]
                rolling_percentage_sums[get_descriptor(kind, rf)][1] += y_disk_off[-1]
            x.append(" "*i) # ugh
            y_tiered.append(None)
            y_disk_off.append(None)

        if averages: 
            x_avg = []
            y_avg_tiered = []
            y_avg_disk_off = [] 
            for kind, num_of_kind in zip(["Cheap", "Expensive"], [num_cheap, num_expensive]): 
                for p in percentages: 
                    x_avg.append(get_descriptor(kind, p))
                    y_avg_tiered.append(rolling_percentage_sums[get_descriptor(kind, p)][0] / num_of_kind)
                    y_avg_disk_off.append(rolling_percentage_sums[get_descriptor(kind, p)][1] / num_of_kind)
            fig, ax = plt.subplots(layout="constrained")
            ax.scatter(y_avg_tiered, x_avg, label="Tiered on")
            ax.scatter(y_avg_disk_off, x_avg, label="Tiered off")
            ax.set_title("Average {} for cheap/expensive queries".format(value), y=1.08)
            ax.set_xlabel("{} as percentage of main".format(value, unit))
            ax.vlines([100], 0, len(x_avg), "r")
            ax.set_ylabel("Query type")
            ax.legend()
            ax.grid(True)
            plt.show()

        else: 
            fig, ax = plt.subplots(layout="constrained")
            ax.scatter(y_tiered, x, label="Tiered on")
            ax.scatter(y_disk_off, x, label="Tiered off")
            
            ax.set_title("{} by query type".format(value), y=1.08)
            ax.set_xlabel("{} as percentage of main".format(value, unit))
            ax.set_ylabel("Query type")
            ax.legend()
            ax.grid(True)
            plt.show()

do_standard()
do_percentage(averages=True)

