"""
Usage Guide for output_results_to_csv.py

This script provides a function to save courier routing solutions in CSV format.

How to use:

1. Import the save_solution function in your main script:
   from output_results_to_csv import save_solution

2. After generating your solution, call the function with these parameters:

   save_solution(courier_orders, instance_folder_path, output_folder_path)

   Parameters:
   - courier_orders: A list of lists. Each inner list represents the orders for a single courier,
     including both pickup and dropoff in the order they are visited.
     Example: [[15, 12, 17, 6, 6, 17, 15, 12], [13, 14, 13, 14]]

   - instance_folder_path: The path to the folder containing the instance data.
     This is used to name the output file.
     Example: "./training_data/b3671e42-6d8d-47d7-a57e-a6b52061010b"

   - output_folder_path: The path where you want to save the solution CSV file.
     Example: "./solutions"

3. The function will create the output folder if it doesn't exist, and save the CSV file
   with the same name as the instance folder.

Example usage:

courier_orders = [[15, 12, 17, 6, 6, 17, 15, 12], [13, 14, 13, 14]]
instance_folder_path = "./training_data/b3671e42-6d8d-47d7-a57e-a6b52061010b"
output_folder_path = "./solutions"

save_solution(courier_orders, instance_folder_path, output_folder_path)

This will create a CSV file named "b3671e42-6d8d-47d7-a57e-a6b52061010b.csv" in the "./solutions" folder,
with content:

ID
1,15,12,17,6,6,17,15,12
2,13,14,13,14

Note: The courier IDs in the CSV start from 1 and correspond to the order of the lists in courier_orders.

To do the feasiblity check, run:
python feasibility_checker.py [folder of testdata, e.g. ./training_data] [solutions folder]
"""

import csv
import os

def output_solution_to_csv(courier_orders, output_file_path):
    with open(output_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the header row
        writer.writerow(["ID"])
        
        for courier_id, orders in enumerate(courier_orders, start=1):
            row = [courier_id] + orders
            writer.writerow(row)

def save_solution(courier_orders, instance_folder_path, output_folder_path):
    # Extract the instance name from the input path
    instance_name = os.path.basename(instance_folder_path)
    
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)
    
    # Define the output file path
    output_file_path = os.path.join(output_folder_path, f"{instance_name}.csv")
    
    # Save the solution to CSV
    output_solution_to_csv(courier_orders, output_file_path)
    print(f"Solution has been written to {output_file_path}")

# Example usage
if __name__ == "__main__":
    # This is just an example. In real use, this would be provided by the main algorithm.
    courier_orders = [[15, 12, 17, 6, 6, 17, 15, 12], [13, 14, 13, 14]]
    instance_folder_path = "./training_data/b3671e42-6d8d-47d7-a57e-a6b52061010b"
    output_folder_path = "./temp_solutions"
    
    save_solution(courier_orders, instance_folder_path, output_folder_path)
