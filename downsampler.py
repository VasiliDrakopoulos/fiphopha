import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog

# Function to downsample data by averaging a certain amount of rows
def downsample_data(data, factor):
    n_rows = data.shape[0]
    
    if factor > n_rows:
        raise ValueError("Downsample factor is larger than the number of rows in the data.")
    
    n_downsampled_rows = n_rows // factor
    downsampled_data = np.mean(
        data[:n_downsampled_rows * factor].reshape(n_downsampled_rows, factor, -1), axis=1
    )
    return downsampled_data

# Process photometry file
def process_downsampling(file_path, downsample_factor):
    try:
        df = pd.read_excel(file_path, sheet_name=None)
        sheets = list(df.keys())
        
        downsampled_data_dict = {}

        for sheet in sheets:
            data = df[sheet].values

            if not np.issubdtype(data.dtype, np.number):
                raise ValueError(f"Non-numeric data found in sheet '{sheet}'. Ensure all data is numeric.")
                
            downsampled_data = downsample_data(data.astype(np.float32), downsample_factor)
            downsampled_data_dict[sheet] = pd.DataFrame(downsampled_data)
        
        output_file_path = file_path.replace('.xlsx', f'_downsampled_{downsample_factor}.xlsx')
        with pd.ExcelWriter(output_file_path) as writer:
            for sheet_name, downsampled_df in downsampled_data_dict.items():
                downsampled_df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        print(f"Downsampled data saved to {output_file_path}")
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
        downsample_factor = simpledialog.askinteger("Downsample Factor", "Enter the downsample factor (e.g., 10):")

        if downsample_factor is None or downsample_factor <= 0:
            raise ValueError("Downsample factor must be a positive integer.")

        output_file = process_downsampling(file_path, downsample_factor)
        if output_file:
            print(f"Downsampled data saved to {output_file}")

    except ValueError as ve:
        print(f"Input error: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")

# GUI setup
def main():
    root = tk.Tk()
    root.title("FiPhoPHA: Downsampler")
    root.geometry("300x300")

    upload_button = tk.Button(root, text="Upload Excel File", command=upload_file)
    upload_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
