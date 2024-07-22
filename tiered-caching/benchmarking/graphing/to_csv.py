files = [
    "final_S1.txt", 
    "final_S2.txt", 
    "final_S3.txt", 
    "final_S4.txt",
    "final_S5.txt", 
    "final_S6.txt", 
    "final_HC1.txt", 
    "final_HC2.txt",
    "final_HC3.txt",
    "final_HC4.txt",
    "final_LR1.txt", 
    "final_LR2.txt",
    "final_HHC1.txt", 
    "final_HHC2.txt",
    "final_HHC3.txt",
    "final_HHC4.txt",
    "final_PT1.txt", 
    "final_PT2.txt",
    "final_PT3.txt",
    "final_PT4.txt",
    "final_IN1.txt", 
    "final_IN2.txt", 
    "final_IN3.txt",
    "final_DCD1.txt", 
    "final_DCD2.txt", 
    "final_DCD3.txt",
    "final_KS1.txt", 
    "final_KS2.txt", 
    "final_KS3.txt",
    "final_EWC1.txt",
    "final_EWC2.txt",
    "final_EWC3.txt",
    "final_EWC4.txt"
    ]

#["final_HC1.txt", "final_HC2.txt","final_HC3.txt","final_HC4.txt"]

#["final_S1.txt", "final_S2.txt", "final_S3.txt", "final_S4.txt", "final_S5.txt", "final_S6.txt"]

#["tc_on_half_concurrency_03.txt", "tc_on_half_concurrency_07.txt", "tc_off_half_concurrency_03.txt", "tc_off_half_concurrency_07.txt"]


#["tc_on_03.txt", "tc_on_07.txt", "tc_off_03.txt", "tc_off_07.txt"]

'''[
    "tc_07_segmented_lock_change_rerun.txt", 
    "tc_07_tsc_lock_per_key.txt", 
    "tc_07_with_query_recompute_moved_out.txt", 
    "tc_07_segmented_lock_change_rerun.txt", 
    "non_tc_07_cache_optimize_removal_flow.txt", 
    "non_tc_07_main.txt", 
]'''

#["non_tc_03_lock_diagnostic.txt", "tc_03_threadlocal_lock_diagnostic.txt", "tc_03_lock_per_key_and_cia.txt", "tc_03_cia_only.txt", "tc_03_final_segmented_locks.txt", "tc_03_no_locks.txt"] #["main_03.txt", "tiered_03.txt"]
'''[
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
]'''

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
