# Created by Meira Forcelini Machado, March 2025, using Excel macros created by M. Alex Coto.
# This script was developed for behavioral data processing in rCPT experiments, converting ABET II raw files into binary files.
# Line 64: change file prefix name to be identified from input folder
# Lines 114 and 115: add input and output folder

import os
import pandas as pd
import numpy as np
import re
import platform

def apply_formulas(df):
    binary_df = pd.DataFrame()
    binary_df['Time'] = df.iloc[:, 0]  # Column A

    # Event mappings
    event_mappings = {
        'TTL #1': 'TTL #1',
        'Hit': 'Hit',
        'Missed Hit': 'Missed Hit',
        'Correct Rejection': 'Correct Rejection',
        'Non Correction Trial Miskake': 'False Alarm',
        'Reward Collected Start ITI': 'Reward Collected Start ITI',
        'Feeder #1': 'Reward Delivery',
        'Correction Trial Mistake': 'Correction Trial Mistake',
        'Correction Trial Correct Rejection': 'Correction Trial Correct Rejection',
        'Centre Screen Touches': 'Centre Screen Touches'  # Simple binary column
    }

    # Create binary columns for each event type
    for event_value, col_name in event_mappings.items():
        binary_df[col_name] = np.where(df.iloc[:, 3] == event_value, 1, 0)

    # Mark Display Image rows (kept as is since it's used for alignment)
    is_display_image = (df.iloc[:, 2] == "Condition Event") & (df.iloc[:, 3] == "Display Image") & (df.iloc[:, 5] == 4)
    binary_df['Display Image Binary'] = np.where(is_display_image, 1, 0)

    # Aligned events
    label_map = {
        "Hit": "Hit",
        "Missed Hit": "Missed Hit",
        "Correct Rejection": "Correct Rejection",
        "False Alarm": "Non Correction Trial Miskake",
    }

    display_indices = df[is_display_image].index
    is_outcome = (df.iloc[:, 2] == "Condition Event") & (5 <= df.iloc[:, 5]) & (df.iloc[:, 5] <= 6)
    outcome_df = df[is_outcome]

    for label, expected_name in label_map.items():
        aligned = np.zeros(len(df))

        for disp_idx in display_indices:
            next_disp = display_indices[display_indices > disp_idx].min() if any(display_indices > disp_idx) else len(df)
            trial_outcomes = outcome_df[(outcome_df.index > disp_idx) & (outcome_df.index < next_disp)]

            if any(trial_outcomes.iloc[:, 3] == expected_name):
                aligned[disp_idx] = 1

        binary_df[f'{label} (with Display)'] = aligned

    return binary_df

def generate_binary_file(input_folder, output_folder, filename_prefix="TCN"):
    input_folder = os.path.normpath(input_folder)
    output_folder = os.path.normpath(output_folder)

    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.startswith(filename_prefix) and file.endswith(".csv"):
            input_path = os.path.join(input_folder, file)

            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                data_start_index = None
                animal_id = None
                date_time = None

                for i, line in enumerate(lines):
                    if "Evnt_Time" in line:
                        data_start_index = i
                        break
                    elif "Animal ID" in line:
                        animal_id = line.strip().split(",")[1].strip()
                    elif "Date/Time" in line:
                        date_time = line.strip().split(",")[1].strip()

                if data_start_index is None:
                    print(f"Skipping file {file}: 'Evnt_Time' column not found.")
                    continue

                df = pd.read_csv(input_path, skiprows=data_start_index, encoding='utf-8')
                binary_df = apply_formulas(df)

                if animal_id and date_time:
                    safe_date_time = re.sub(r'[: /]', '_', date_time)
                    output_filename = f"{animal_id}_{safe_date_time}.csv"
                else:
                    output_filename = f"Binary_{file}"

                output_path = os.path.join(output_folder, output_filename)
                binary_df.to_csv(output_path, index=False)
                print(f"Successfully processed: {file} -> {output_filename}")

            except Exception as e:
                print(f"Error processing file {file}: {str(e)}")
                continue

if __name__ == "__main__":
    # Example paths - replace with your actual paths
    input_path = "add your folder path"
    output_path = "add your folder path"

    generate_binary_file(input_folder=input_path, output_folder=output_path)
