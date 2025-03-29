import numpy as np
import pandas as pd
from sklearn.utils import resample
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import multiprocessing
import sys
from multiprocessing import Pool, cpu_count

# Bootstrap Confidence Interval with sqrt adjustment
def boot_CI(data, n_resamples=1000, confidence_level=0.95):
    try:
        boot_means = np.array([np.mean(resample(data)) for _ in range(n_resamples)])
        lower_bound = np.percentile(boot_means, (1 - confidence_level) / 2 * 100)
        upper_bound = np.percentile(boot_means, (1 + confidence_level) / 2 * 100)
        n = len(data)
        sqrt_adjustment = np.sqrt(n / (n - 1)) if n > 1 else 1  
        return lower_bound * sqrt_adjustment, upper_bound * sqrt_adjustment
    except Exception as e:
        print(f"Error in boot_CI: {e}")
        raise

# Permutation Test
def permutation_test(group1, group2, period, n_permutations=1000):
    try:
        data1 = group1[period[0]:period[1], :].mean(axis=0)
        data2 = group2[period[0]:period[1], :].mean(axis=0)
        actual_diff = np.mean(data1) - np.mean(data2)

        pooled_data = np.hstack((data1, data2))
        perm_diffs = []
        for _ in range(n_permutations):
            np.random.shuffle(pooled_data)
            perm_group1 = pooled_data[:len(data1)]
            perm_group2 = pooled_data[len(data1):]
            perm_diffs.append(np.mean(perm_group1) - np.mean(perm_group2))
        perm_diffs = np.array(perm_diffs)
        p_value = np.mean(np.abs(perm_diffs) >= np.abs(actual_diff))
        return actual_diff, p_value
    except Exception as e:
        print(f"Error in permutation_test: {e}")
        raise

# Analyze each time point
def analyze_time_point(args):
    try:
        group1, group2, t, n_resamples, confidence_level = args
        ci1 = boot_CI(group1[t, :], n_resamples, confidence_level)
        ci2 = boot_CI(group2[t, :], n_resamples, confidence_level)

        group_diff = group1[t, :] - group2[t, :]
        diff_CI = boot_CI(group_diff, n_resamples, confidence_level)

        significant_from_baseline_1 = (ci1[0] > 0 and ci1[1] > 0) or (ci1[0] < 0 and ci1[1] < 0)
        significant_from_baseline_2 = (ci2[0] > 0 and ci2[1] > 0) or (ci2[0] < 0 and ci2[1] < 0)
        significant_between_groups = (diff_CI[0] > 0 or diff_CI[1] < 0) 

        return t, significant_between_groups, (ci1, ci2, diff_CI), significant_from_baseline_1, significant_from_baseline_2
    except Exception as e:
        print(f"Error in analyze_time_point: {e}")
        raise

# Apply consecutive significance threshold
def apply_consecutive_threshold(significance_map, threshold):
    significance_map = np.array(significance_map, dtype=int)
    filtered_map = np.zeros_like(significance_map, dtype=int)

    indices = np.where(significance_map == 1)[0]
    if len(indices) == 0:
        return filtered_map

    breaks = np.where(np.diff(indices) > 1)[0]
    start_indices = np.insert(indices[breaks + 1], 0, indices[0])
    end_indices = np.append(indices[breaks], indices[-1])

    for start, end in zip(start_indices, end_indices):
        length = end - start + 1
        if length >= threshold:
            filtered_map[start:end + 1] = 1

    return filtered_map

# Analyze photometry file 
def analyze_photometry_data(groups, baseline_period, comparison_period, n_resamples=1000, confidence_level=0.95, 
                            n_permutations=1000, consecutive_threshold=1):
    try:
        n_timepoints = groups[0].shape[0]
        significance_maps_between_groups = {}
        significance_from_baseline_map = np.zeros((n_timepoints, len(groups)), dtype=int)

        results = {}

        with Pool(processes=cpu_count()) as pool:
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    group1, group2 = groups[i], groups[j]

                    if group1.shape[1] != group2.shape[1]:
                        raise ValueError(f"Group {i+1} and Group {j+1} have different numbers of columns. "
                                         "Ensure both groups have the same number of trials/animals.")

                    args = [(group1, group2, t, n_resamples, confidence_level) for t in range(n_timepoints)]  
                    analysis_results = pool.map(analyze_time_point, args)

                    significance_map = np.zeros(n_timepoints)

                    for t, significant_between_groups, (ci1, ci2, diff_CI), sig_from_baseline_1, sig_from_baseline_2 in analysis_results:
                        significance_map[t] = int(significant_between_groups)
                        significance_from_baseline_map[t, i] = int(sig_from_baseline_1) 
                        significance_from_baseline_map[t, j] = int(sig_from_baseline_2)  

                        comparison_key = f'Group {i + 1} vs Group {j + 1}'
                        if comparison_key not in results:
                            results[comparison_key] = {}
                        results[comparison_key]['CIs'] = (ci1, ci2, diff_CI)

                    significance_map = apply_consecutive_threshold(significance_map, consecutive_threshold)
                    significance_maps_between_groups[comparison_key] = significance_map

                    baseline_diff, baseline_p_value = permutation_test(group1, group2, baseline_period, n_resamples)
                    comparison_diff, comparison_p_value = permutation_test(group1, group2, comparison_period, n_resamples)

                    results[comparison_key]['Baseline Permutation Test'] = (baseline_diff, baseline_p_value)
                    results[comparison_key]['Comparison Permutation Test'] = (comparison_diff, comparison_p_value)

        for i in range(len(groups)):
            significance_from_baseline_map[:, i] = apply_consecutive_threshold(significance_from_baseline_map[:, i], consecutive_threshold)

        return results, significance_maps_between_groups, significance_from_baseline_map
    except Exception as e:
        print(f"Error in analyze_photometry_data: {e}")
        raise

# Process photometry file  
def process_photometry_file(file_path, baseline_period, comparison_period, n_resamples=1000, confidence_level=0.95, n_permutations=1000, consecutive_threshold=1):
    try:
        df = pd.read_excel(file_path, sheet_name=None)
        sheets = list(df.keys())

        group_data = []
        for sheet in sheets:
            data = df[sheet].apply(pd.to_numeric, errors='coerce')  
            data = data.dropna()  
            group_data.append(data.values.astype(np.float32))  

        results, significance_maps_between_groups, significance_from_baseline_map = analyze_photometry_data(
            group_data, baseline_period, comparison_period, n_resamples, confidence_level, n_permutations, consecutive_threshold
        )

        output_results = []
        for comparison, details in results.items():
            if 'Baseline Permutation Test' in details and 'Comparison Permutation Test' in details:
                baseline_diff, baseline_p_value = details['Baseline Permutation Test']
                comparison_diff, comparison_p_value = details['Comparison Permutation Test']
                sig_points_between_groups = [i for i, val in enumerate(significance_maps_between_groups[comparison]) if val == 1]

                output_results.append({
                    'Comparison': comparison,
                    'Baseline Mean Difference': baseline_diff,
                    'Baseline P-Value': baseline_p_value,
                    'Comparison Mean Difference': comparison_diff,
                    'Comparison P-Value': comparison_p_value,
                    'Significant Time Points Between Groups': ', '.join(map(str, sig_points_between_groups))
                })

        results_df = pd.DataFrame(output_results)

        settings_df = pd.DataFrame({
            'Setting': ['Confidence Level', 'Number of Resamples', 'Number of Permutations', 'Consecutive Threshold', 'Baseline Period', 'Comparison Period'],
            'Value': [confidence_level, n_resamples, n_permutations, consecutive_threshold, str(baseline_period), str(comparison_period)]
        })

        output_file_path = file_path.replace('.xlsx', '_results.xlsx')
        with pd.ExcelWriter(output_file_path) as writer:
            results_df.to_excel(writer, index=False, sheet_name='Results')

            for comparison, sig_map in significance_maps_between_groups.items():
                pd.DataFrame(sig_map, columns=[comparison]).to_excel(writer, index=False, sheet_name=comparison)

            pd.DataFrame(significance_from_baseline_map, columns=[f'Group {i+1}' for i in range(len(group_data))]).to_excel(writer, index=False, sheet_name='Significance From Baseline')

            settings_df.to_excel(writer, index=False, sheet_name='Analysis Settings')

        print(f"Results saved to {output_file_path}")
        return results, significance_maps_between_groups, significance_from_baseline_map
    except Exception as e:
        print(f"Error in process_photometry_file: {e}")
        raise

# Upload file for GUI
def upload_file(confidence_level_entry, resamples_entry, permutations_entry, consecutive_threshold_entry):
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        return

    try:
        confidence_level = float(confidence_level_entry.get()) / 100.0 
        n_resamples = int(resamples_entry.get())
        n_permutations = int(permutations_entry.get())
        consecutive_threshold = int(consecutive_threshold_entry.get())

        df = pd.read_excel(file_path, sheet_name=None)
        max_rows = df[list(df.keys())[0]].shape[0]

        baseline_start = simpledialog.askinteger("Baseline Start", "Enter the baseline start row:")
        baseline_end = simpledialog.askinteger("Baseline End", "Enter the baseline end row:")
        comparison_start = simpledialog.askinteger("Comparison Start", "Enter the comparison start row:")
        comparison_end = simpledialog.askinteger("Comparison End", f"Enter the comparison end row (max {max_rows - 1}):")

        if baseline_start is None or baseline_end is None or comparison_start is None or comparison_end is None:
            raise ValueError("All row indices must be provided.")

        if (baseline_start < 0 or baseline_end < 0 or
                comparison_start < 0 or comparison_end < 0 or
                baseline_end > max_rows or comparison_end > max_rows):
            raise ValueError(f"Row must be non-negative and less than {max_rows}.")

        baseline_period = (baseline_start, baseline_end)
        comparison_period = (comparison_start, comparison_end)

        process_photometry_file(
            file_path, baseline_period, comparison_period, 
            n_resamples, confidence_level, n_permutations, consecutive_threshold
        )
   
    except ValueError as ve:
        print(f"Input error: {ve}")
        messagebox.showerror("Input Error", str(ve))
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        messagebox.showerror("File Error", "The specified file was not found.")
    except pd.errors.EmptyDataError:
        print("The input file is empty or invalid.")
        messagebox.showerror("Data Error", "The input file is empty or invalid.")
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Processing Error", str(e))

# GUI setup
def run_gui():
    root = tk.Tk()
    root.title("FiPhoPHA: Within-Groups Bootstrapped Confidence Intervals and Permutation Tests")
    root.geometry("350x350")

    tk.Label(root, text="Confidence Level (%)").grid(row=0, column=0)
    confidence_level_entry = tk.Entry(root)
    confidence_level_entry.grid(row=0, column=1)

    tk.Label(root, text="Number of Resamples").grid(row=1, column=0)
    resamples_entry = tk.Entry(root)
    resamples_entry.grid(row=1, column=1)

    tk.Label(root, text="Number of Permutations").grid(row=2, column=0)
    permutations_entry = tk.Entry(root)
    permutations_entry.grid(row=2, column=1)

    tk.Label(root, text="Consecutive Threshold").grid(row=3, column=0)
    consecutive_threshold_entry = tk.Entry(root)
    consecutive_threshold_entry.grid(row=3, column=1)

    upload_button = tk.Button(root, text="Upload File", command=lambda: upload_file(
        confidence_level_entry, resamples_entry, permutations_entry, consecutive_threshold_entry))
    upload_button.grid(row=4, columnspan=2)

    root.mainloop()

def main():
    print("Running within-groups bootstrap and permutation tests...")
    run_gui()

if __name__ == "__main__":
    if sys.platform == 'darwin':  
        multiprocessing.set_start_method("spawn", force=True)  
    
    main()  
