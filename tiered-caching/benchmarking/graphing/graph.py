import matplotlib.pyplot as plt 
import pandas as pd 
import numpy as np

plt.rcParams['font.size'] = 9

# run to_csv.py to refresh this file if new results are added
types_dict = {'Percentage': str}
df = pd.read_csv("all_results.csv", dtype=types_dict) 

y_values = [
    "Min Throughput",
    "Median Throughput", 
    "20th percentile latency",
    "50th percentile latency", 
    "75th percentile latency",
    "90th percentile latency", 
    "99th percentile latency", 
    "100th percentile latency"
]

runs_to_display = ["final_EWC1", "final_EWC2", "final_EWC3", "final_EWC4", "final_S1", "final_S3"]
#["final_KS1", "final_KS2", "final_KS3", "final_S1", "final_S3", "final_S5"]
#["final_S1", "final_S2", "final_S3", "final_S4", "final_S5", "final_S6", "final_DCD1", "final_DCD2", "final_DCD3"]
#["final_DCD1", "final_DCD2", "final_DCD3"]
#["final_S1", "final_S2", "final_S3", "final_S4", "final_S5", "final_S6", "final_DCD1", "final_DCD2", "final_DCD3"]
#["final_HC1", "final_HC2","final_HC3","final_HC4"]
#["final_S1", "final_S2", "final_S3", "final_S4", "final_S5", "final_S6"]
#["final_IN1", "final_IN2", "final_IN3"]
#["final_S5", "final_PT1", "final_PT2","final_PT3","final_PT4"]
#["final_HHC1", "final_HHC2","final_HHC3","final_HHC4"]
#["final_LR1", "final_LR2"]
#["final_S1", "final_S2", "final_S3", "final_S4", "final_S5", "final_S6"]
#["tc_on_half_concurrency_03", "tc_off_half_concurrency_03","tc_on_half_concurrency_07", "tc_off_half_concurrency_07"] #["tc_on_03", "tc_off_03","tc_on_07", "tc_off_07"]

run_name_map = {
    "final_S1":"Standard, TC on, rf=0%", 
    "final_S2":"Standard, TC off, rf=0%",
    "final_S3":"Standard, TC on, rf=30%",
    "final_S4":"Standard, TC off, rf=30%", 
    "final_S5":"Standard, TC on, rf=70%",
    "final_S6":"Standard, TC off, rf=70%",
    "final_HC1":"High concurrency, TC on, rf=30%", 
    "final_HC2":"High concurrency, TC off, rf=30%",
    "final_HC3":"High concurrency, TC on, rf=70%",
    "final_HC4":"High concurrency, TC off, rf=70%",
    "final_HHC1":"Higher concurrency, TC on, rf=30%", 
    "final_HHC2":"Higher concurrency, TC off, rf=30%",
    "final_HHC3":"Higher concurrency, TC on, rf=70%",
    "final_HHC4":"Higher concurrency, TC off, rf=70%",
    "final_PT1":"Policy threshold=3ms, rf=70%", 
    "final_PT2":"Policy threshold=10ms, rf=70%",
    "final_PT3":"Policy threshold=20ms, rf=70%",
    "final_PT4":"Policy threshold=50ms, rf=70%",
    "final_LR1":"Long running, TC on, rf=70%",
    "final_LR2":"Long running, TC off, rf=70%",
    "final_IN1":"Invalidation interval=1m, rf=70%",
    "final_IN2":"Invalidation interval=10s, rf=70%",
    "final_IN3":"Invalidation interval=1s, rf=70%",
    "final_DCD1":"Disk cache disabled, rf=0%",
    "final_DCD2":"Disk cache disabled, rf=30%",
    "final_DCD3":"Disk cache disabled, rf=70%",
    "final_KS1":"Keystore enabled, rf=0%", 
    "final_KS2":"Keystore enabled, rf=30%",
    "final_KS3":"Keystore enabled, rf=70%",
    "final_EWC1":"Concurrency=3, write threads=5, rf=0%",
    "final_EWC2":"Concurrency=3, write threads=5, rf=30%",
    "final_EWC3":"Concurrency=3, write threads=5, segments=32, rf=0%",
    "final_EWC4":"Concurrency=3, write threads=5, segments=32, rf=30%",
}

'''tc_on_runs = []
for run_name in run_name_map: 
    if not "TC off" in run_name_map[run_name]: 
        tc_on_runs.append(run_name)'''

tc_on_off_pairs = { 
    "final_S1":["final_S2", "0%"],
    "final_S3":["final_S4", "30%"],
    "final_S5":["final_S6", "70%"],
    "final_HC1":["final_HC2", "30%"],
    "final_HC3":["final_HC4", "70%"],
    "final_HHC1":["final_HHC2", "30%"],
    "final_HHC3":["final_HHC4","70%"],
    "final_LR1":["final_LR2","70%"]
} # TC on one : [TC off one, name to display]

tc_disabled_off_pairs = { 
    "final_DCD1":["final_S2", "0%"],
    "final_DCD2":["final_S4","30%"],
    "final_DCD3":["final_S6", "70%"],
} # TC on but disk cache disabled : TC off

pt_pairs = {
    "final_PT1":["final_S5", "3ms"],
    "final_PT2":["final_S5", "10ms"],
    "final_PT3":["final_S5", "20ms"],
    "final_PT4":["final_S5", "50ms"],
}

keystore_pairs = {
    "final_KS1":["final_S1", "0%"],
    "final_KS2":["final_S3","30%"],
    "final_KS3":["final_S5", "70%"],
} # keystore on : keystore off (but disk on)

ewc_pairs = {
    "final_EWC1":["final_S1", "0%, segments=16"],
    "final_EWC2":["final_S3", "30%, segments=16"],
    "final_EWC3":["final_S1", "0%, segments=32"],
    "final_EWC4":["final_S3", "30%, segments=32"]
}

cheap_queries = ["cheap-dropoff", "cheap-pickup", "cheap-total-amount", "cheap-fare-amount", "cheap-tip-amount"]
medium_queries = ["auto-date-histogram", "autohisto-agg", "date-histogram-fixed-interval", "date-histogram-calendar-interval", "date-histogram-agg"]
expensive_queries = ["auto-date-histogram-with-tz", "date-histogram-fixed-interval-with-tz", "date-histogram-calendar-interval-with-tz"]

def get_query_kind(query): 
    if query in cheap_queries: 
        return "Cheap"
    if query in medium_queries: 
        return "Medium"
    return "Expensive"

# Make a grouped bar chart, where the group is the task, the different entries in the groups are the runs, 
# and the y axis is the entry in y_values 
#query_groups = list(df[df["Run"] == runs_to_display[0]]["Operation"].unique())
query_groups = cheap_queries + medium_queries + expensive_queries
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

cs = ["g", "y", "b", "r"]

run_types = ["tiered", "disk_off", "main"]
percentages = ["03", "07"] # TODO: it's parsing as int not string #["03", "07"]#["00", "01", "03", "065"]
pct_label_map = {"03":"30%", "07":"70%"} #{"03":"30%", "07":"70%"} #{"00":"0%", "01":"10%", "03":"30%", "065":"65%"}

# based on https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html
def do_standard(log=True): 
    for value in y_values: 
        run_values = {}
        val_df = df[df["Task"] == value]
        unit = val_df["Unit"].unique()[0]
        for run in runs_to_display: 
            run_df = val_df[val_df["Run"] == run]
            print(run)
            run_values[run] = tuple([run_df[run_df["Operation"] == op]["Time"].iloc[0] for op in query_groups])

        x = np.arange(len(query_groups))
        width = 0.15
        multiplier = 0
        print(run_values)

        fig, ax = plt.subplots(layout="constrained") 
        for run_title, time in run_values.items(): 
            offset = width * multiplier 
            print(run_title, time)
            rects = ax.barh(x + offset, time, width, label=run_name_map.get(run_title, run_title)) 
            ax.bar_label(rects, padding=3, fmt="%.1f") # fmt="%.2e", rotation=90
            multiplier += 1
        
        ax.set_title("{} by query type".format(value), y=1.08)
        ax.set_yticks(x+width, query_groups)
        if unit == "ms": 
            if log:
                ax.set_xscale("log")
                ax.set_xlabel("{} ({}, log)".format(value, unit))
            else: 
                ax.set_xlabel("{} ({})".format(value, unit))
        else: 
            ax.set_xlabel("{} ({})".format(value, unit))
        ax.legend()
        ax.grid(True)
        plt.show()

def get_descriptor(kind, percentage): 
    return "{}, hit ratio = {}".format(kind, percentage)

def get_pair_descriptor(query_type, numerator, denominator): 
    return "query={}, num={}, denom={}".format(query_type, numerator, denominator)

def do_percentage(pairs, averages=False, stack_percentiles=None): 
    # pairs argument: dict of keys of TC on (or analogous) runs (numerator), values are TC off runs with matching params (denominator)
    # plot percentage scatter plot 
    fig, ax = plt.subplots(layout="constrained") 
    # insert empty one in between each query type to space out groups?
    for value in y_values: 
        run_values = {}
        print("df\n", df)
        val_df = df[df["Task"] == value] # throughput, latency, etc
        unit = val_df["Unit"].unique()[0]
        
        x = []
        y_tiered = []

        x_avg = [] # for average of all expensive queries 0%, 10%, ... 
        rolling_percentage_sums = {} # contains rolling sum of percentages for each category (ex: cheap queries with 65% rf)
        for kind in ["Cheap", "Medium", "Expensive"]: 
            '''for p in percentages: 
                rolling_percentage_sums[get_descriptor(kind, p)] = [0, 0] # tiered sum, disk off sum'''
            for numerator in pairs: 
                denominator = pairs[numerator][0]
                display_name = pairs[numerator][1]
                if numerator in runs_to_display and denominator in runs_to_display: 
                    rolling_percentage_sums[get_descriptor(kind, display_name)] = 0
                

        # split into cheap (approx < 10 ms), medium (10 ms - 100 ms), and expensive (> 100 ms) at p90
        num_expensive = 0
        num_medium = 0
        num_cheap = 0
        for i, query_type in enumerate(query_groups): 
            kind = get_query_kind(query_type)
            if kind == "Cheap": 
                num_cheap += 1 
            elif kind == "Medium": 
                num_medium += 1
            else:
                num_expensive += 1

            q_df = val_df[val_df["Operation"] == query_type]
            '''for rf in percentages: 
                print("rf = ", rf)
                print("q_df\n", q_df)
                rf_df = q_df[q_df["Percentage"] == rf]
                print("rf_df\n", rf_df)
                tiered_time = rf_df[rf_df["Run type"] == "tc_on_half_concurrency"]["Time"].iloc[0]
                #disk_off_time = rf_df[rf_df["Run type"] == "disk_off"]["Time"].iloc[0]
                main_time = rf_df[rf_df["Run type"] == "tc_off_half_concurrency"]["Time"].iloc[0]
                x.append(get_descriptor(query_type, rf))
                y_tiered.append(tiered_time / main_time * 100)
                #y_disk_off.append(disk_off_time / main_time * 100)
                rolling_percentage_sums[get_descriptor(kind, rf)][0] += y_tiered[-1]
                #rolling_percentage_sums[get_descriptor(kind, rf)][1] += y_disk_off[-1]'''
            for numerator in pairs: 
                denominator = pairs[numerator][0]
                display_name = pairs[numerator][1]
                if numerator in runs_to_display and denominator in runs_to_display: 
                    numerator_df = q_df[q_df["Run"] == numerator]
                    denominator_df = q_df[q_df["Run"] == denominator]
                    print("Numerator df = ")
                    print(numerator_df)
                    print("Denominator df = ")
                    print(denominator_df)
                    tiered_time = numerator_df["Time"].iloc[0]
                    main_time = denominator_df["Time"].iloc[0]
                    x.append(get_descriptor(query_type, display_name))
                    #x.append(get_pair_descriptor(query_type, numerator, denominator))
                    y_tiered.append(tiered_time / main_time * 100)
                    rolling_percentage_sums[get_descriptor(kind, display_name)] += y_tiered[-1]
                    #rolling_percentage_sums[get_pair_descriptor(kind, numerator, denominator)] += y_tiered[-1]

            x.append(" "*i) # ugh
            y_tiered.append(None)

        print("cheap:{}, medium:{}, expensive:{}".format(num_cheap, num_medium, num_expensive))
        if averages: 
            x_avg = []
            y_avg_tiered = []
            for kind, num_of_kind in zip(["Cheap", "Medium", "Expensive"], [num_cheap, num_medium, num_expensive]): 
                for numerator in pairs: 
                    denominator = pairs[numerator][0]
                    display_name = pairs[numerator][1]
                    if numerator in runs_to_display and denominator in runs_to_display: 
                        x_avg.append(get_descriptor(kind, display_name))
                        y_avg_tiered.append(rolling_percentage_sums[get_descriptor(kind, display_name)] / num_of_kind)
                        #x_avg.append(get_pair_descriptor(kind, numerator, denominator))
                        #y_avg_tiered.append(rolling_percentage_sums[get_pair_descriptor(kind, numerator, denominator)] / num_of_kind)

                '''for p in percentages: 
                    x_avg.append(get_descriptor(kind, p))
                    y_avg_tiered.append(rolling_percentage_sums[get_descriptor(kind, p)][0] / num_of_kind)
                    #y_avg_disk_off.append(rolling_percentage_sums[get_descriptor(kind, p)][1] / num_of_kind)'''
            fig, ax = plt.subplots(layout="constrained")
            ax.scatter(y_avg_tiered, x_avg, label="Tiered on")
            #ax.scatter(y_avg_disk_off, x_avg, label="Tiered off")
            ax.set_title("Average {} for cheap/medium/expensive queries".format(value), y=1.08)
            ax.set_xlabel("{} as percentage of baseline".format(value, unit))
            ax.vlines([100], 0, len(x_avg), "r")
            ax.set_xlim(right=max(max_list(y_avg_tiered), 110))
            ax.set_ylabel("Query type")
            #ax.legend()
            ax.grid(True)
            #plt.savefig("plots/{}_{}_percentages.png".format(base_plot_name, value))
            plt.show()

        else: 
            if stack_percentiles is not None: 
                raise Exception("Stack percentiles can only be passed when averages=True!")
                return
            fig, ax = plt.subplots(layout="constrained")
            ax.vlines([100], 0, len(x), "r")
            print("y tiered = ", y_tiered)
            ax.set_xlim(0, max(max_list(y_tiered), 110))
            ax.scatter(y_tiered, x, label="Tiered on")
            #ax.scatter(y_disk_off, x, label="Tiered off")
            
            ax.set_title("{} by query type".format(value), y=1.08)
            ax.set_xlabel("{} as percentage of TC off".format(value, unit))
            ax.set_ylabel("Query type")
            
            #ax.legend()
            ax.grid(True)
            #plt.savefig("plots/{}_{}_percentages_averaged.png".format(base_plot_name, value))

            plt.show()


def multi_series_averaged_percentages(series_list, pairs): 
    # series_list contains tuples of form ("final_S6", "20th percentile latency") which will be shown on the same graph as if produced by do_percentage
    cs = ["r", "orange", "y", "g", "b", "purple"]
    if len(series_list) > len(cs): 
        raise Exception("Too many series list entries, max is len(cs)")
    
    fig, ax = plt.subplots(layout="constrained") 

    for series, color in zip(series_list, cs): 
        run = series[0]
        value = series[1]
        print("df\n", df)
        val_df = df[df["Task"] == value] # throughput, latency, etc
        unit = val_df["Unit"].unique()[0]
        
        x = []
        y_tiered = []

        x_avg = [] # for average of all expensive queries 0%, 10%, ... 
        rolling_percentage_sums = {} # contains rolling sum of percentages for each category (ex: cheap queries with 65% rf)
        for kind in ["Cheap", "Medium", "Expensive"]: 
            for numerator in pairs: 
                denominator = pairs[numerator][0]
                display_name = pairs[numerator][1]
                if numerator in runs_to_display and denominator in runs_to_display: 
                    rolling_percentage_sums[get_descriptor(kind, display_name)] = 0
                

        # split into cheap (approx < 10 ms), medium (10 ms - 100 ms), and expensive (> 100 ms) at p90
        num_expensive = 0
        num_medium = 0
        num_cheap = 0
        for i, query_type in enumerate(query_groups): 
            kind = get_query_kind(query_type)
            if kind == "Cheap": 
                num_cheap += 1 
            elif kind == "Medium": 
                num_medium += 1
            else:
                num_expensive += 1

            q_df = val_df[val_df["Operation"] == query_type]
            for numerator in pairs: 
                denominator = pairs[numerator][0]
                display_name = pairs[numerator][1]
                if numerator in runs_to_display and denominator in runs_to_display: 
                    numerator_df = q_df[q_df["Run"] == numerator]
                    denominator_df = q_df[q_df["Run"] == denominator]
                    print("Numerator df = ")
                    print(numerator_df)
                    print("Denominator df = ")
                    print(denominator_df)
                    tiered_time = numerator_df["Time"].iloc[0]
                    main_time = denominator_df["Time"].iloc[0]
                    x.append(get_descriptor(query_type, display_name))
                    #x.append(get_pair_descriptor(query_type, numerator, denominator))
                    y_tiered.append(tiered_time / main_time * 100)
                    rolling_percentage_sums[get_descriptor(kind, display_name)] += y_tiered[-1]
                    #rolling_percentage_sums[get_pair_descriptor(kind, numerator, denominator)] += y_tiered[-1]

            x.append(" "*i) # ugh
            y_tiered.append(None)

        x_avg = []
        y_avg_tiered = []
        for kind, num_of_kind in zip(["Cheap", "Medium", "Expensive"], [num_cheap, num_medium, num_expensive]): 
            for numerator in pairs: 
                denominator = pairs[numerator][0]
                display_name = pairs[numerator][1]
                if numerator in runs_to_display and denominator in runs_to_display: 
                    x_avg.append(get_descriptor(kind, display_name))
                    y_avg_tiered.append(rolling_percentage_sums[get_descriptor(kind, display_name)] / num_of_kind)
        ax.scatter(y_avg_tiered, x_avg, label=value, c=color)
        ax.vlines([100], 0, len(x_avg), "r")
        #ax.set_xlim(right=max(max_list(y_avg_tiered), 110))
        ax.set_ylabel("Query type")
        
    ax.legend()
    ax.grid(True)
    ax.set_title("Average latencies compared to baseline for cheap/medium/expensive queries".format(value), y=1.08)
    ax.set_xlabel("Latency as percentage of baseline".format(value, unit))
    plt.show()
    

def max_list(l): 
    max_val = -1
    for val in l: 
        if val is not None: 
            if val > max_val: 
                max_val = val
    return max_val

#do_standard(log=False)
#do_percentage(tc_disabled_off_pairs, averages=True) # dont include p100 as it makes the graph impossible to read
series_list = [
    ("", "20th percentile latency"), # todo: first arg doesnt work yet
    ("", "50th percentile latency"),
    ("", "75th percentile latency"),
    ("", "90th percentile latency"),
    ("", "99th percentile latency"),
]
p100_list = [
    ("", "100th percentile latency")
]
multi_series_averaged_percentages(series_list, ewc_pairs)
multi_series_averaged_percentages(p100_list, ewc_pairs)
#do_percentage(pt_pairs, averages=True)
