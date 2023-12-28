files = [
    "tiered_00.txt",
    "tiered_01.txt",
    "tiered_03.txt",
    "tiered_065.txt",
    "tiered_00_old.txt",
    "tiered_01_old.txt",
    "tiered_03_old.txt",
    "tiered_065_old.txt",
    "disk_off_00.txt",
    "disk_off_01.txt",
    "disk_off_03.txt",
    "disk_off_065.txt",
    "main_00.txt",
    "main_01.txt",
    "main_03.txt",
    "main_065.txt",
] 

'''"tiered_jar_disk_off_rf00.txt", 
    "tiered_jar_disk_off_rf01.txt", 
    "tiered_jar_disk_off_rf03.txt", 
    "tiered_jar_disk_off_rf065.txt", 
    "tiered_jar_disk_on_rf00.txt", 
    "tiered_jar_disk_on_rf01.txt", 
    "tiered_jar_disk_on_rf03.txt", 
    "tiered_jar_disk_on_rf065.txt",
    "distance_test_main_october_00.txt"'''

''' "tiered_00_400iter.txt",
    "tiered_01_400iter.txt",
    "tiered_03_400iter.txt",
    "tiered_065_400iter.txt",'''
combo_fp = "all_results.csv"
combo_header = ["Run", "Task", "Operation", "Time", "Unit", "Percentage", "Run type"]
with open(combo_fp, "w") as f: 
    f.write(",".join(combo_header))
    f.write("\n")


header = [["Task", "Operation", "Time", "Unit"]]
for fp in files: 
    lines = [] 
    out_fp = fp.split(".")[0] + ".csv"
    with open(fp, "r") as f: 
        for line in f: 
            terms = line.split("|")
            line_list = []
            for term in terms: 
                if len(term.strip()) > 0:
                    line_list.append(term.strip())
            lines.append(line_list) 
    with open(out_fp, "w") as f: 
        for line in header + lines: 
            f.write(",".join(line))
            f.write("\n")
    with open(combo_fp, "a+") as f: 
        for line in lines: 
            aug_line = [fp.split(".")[0]] + line
            for i in range(len(aug_line)): 
                if aug_line[i].startswith("expensive"): 
                    aug_line[i] = "_".join(aug_line[i].split("-")[1:])
            # also add in percentage and which branch it is, based on run name (first entry in aug_line)
            percentage = aug_line[0].split("_")[-1]
            run_type = "_".join(aug_line[0].split("_")[:-1])
            aug_line.append(percentage)
            aug_line.append(run_type)
            f.write(",".join(aug_line))
            f.write("\n")
