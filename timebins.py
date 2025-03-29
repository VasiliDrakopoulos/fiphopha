import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog

# Function to calculate mean values for specified time bins
def calculate_means_in_time_bins(data, time_bins):
    bin_means = []
    
    for bin_start, bin_end in time_bins:
        bin_data = data[bin_start:bin_end + 1, :]
        bin_mean = np.mean(bin_data, axis=0)
        bin_means.append(bin_mean)
    
    return np.array(bin_means)

# Process photometry file 
def process_time_bins(file_path, time_bins, settings_info):
    try:
        df = pd.read_excel(file_path, sheet_name=None)
        sheets = list(df.keys())
        
        time_bin_means_dict = {}

        for sheet in sheets:
            data = df[sheet].values
            if not np.issubdtype(data.dtype, np.number):
                raise ValueError(f"Non-numeric data found in sheet '{sheet}'. Ensure all data is numeric.")

            time_bin_means = calculate_means_in_time_bins(data.astype(np.float32), time_bins)
            time_bin_means_dict[sheet] = pd.DataFrame(time_bin_means)
        
        output_file_path = file_path.replace('.xlsx', '_time_bin_means.xlsx')
        with pd.ExcelWriter(output_file_path) as writer:
            for sheet_name, bin_means_df in time_bin_means_dict.items():
                bin_means_df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            settings_df = pd.DataFrame.from_dict(settings_info, orient="index", columns=["Value"])
            settings_df.to_excel(writer, sheet_name="Settings", index=True)

        print(f"Time bin means and settings saved to {output_file_path}")
        return output_file_path

    except FileNotFoundError:
        print("The specified file was not found.")
    except ValueError as ve:
        print(f"Input error: {ve}")
    except Exception as e:
        print(f"An error occurred during processing: {e}")

# Upload file for GUI
def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path, sheet_name=None)
        max_rows = df[list(df.keys())[0]].shape[0]
        print(f"Maximum rows (time points): {max_rows}")
        
        time_bins = []
        settings_info = {}

        num_bins = simpledialog.askinteger("Number of Time Bins", "Enter the number of time bins:")
        settings_info["Number of Time Bins"] = num_bins

        if num_bins is None or num_bins <= 0:
            raise ValueError("Number of time bins must be a positive integer.")

        for i in range(num_bins):
            bin_start = simpledialog.askinteger(f"Time Bin {i + 1} Start", "Enter the start row:")
            bin_end = simpledialog.askinteger(f"Time Bin {i + 1} End", "Enter the end row:")

            if bin_start is None or bin_end is None:
                raise ValueError("Both start and end row must be provided.")
            
            if bin_start < 0 or bin_end >= max_rows:
                raise ValueError(f"Row values must be between 0 and {max_rows - 1}.")
            
            if bin_start > bin_end:
                raise ValueError("Start row must be less than or equal to end row.")
            
            time_bins.append((bin_start, bin_end))
            settings_info[f"Time Bin {i + 1} Start"] = bin_start
            settings_info[f"Time Bin {i + 1} End"] = bin_end

        output_file = process_time_bins(file_path, time_bins, settings_info)
        if output_file:
            print(f"Time bin means and settings saved to {output_file}")

    except ValueError as ve:
        print(f"Input error: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")

# GUI setup
def main():
    root = tk.Tk()
    root.title("FiPhoPHA: Mean Time Bins")
    root.geometry("300x300")

    upload_button = tk.Button(root, text="Upload Excel File", command=upload_file)
    upload_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
