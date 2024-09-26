# Delivery Routing Optimization

This project implements a heuristic greedy algorithm for optimizing delivery routes. It includes various components for data processing, solution generation, and feasibility checking.

## Project Structure

```
├── heuristic_greedy.py         # Main file containing the greedy heuristic algorithm
├── assignment_problem.py       # Implements the assignment algorithm
├── Courier.py                  # Defines the Courier data class
├── Delivery.py                 # Defines the Delivery data class
├── Route.py                    # Defines the Route data class
├── read_data.py                # Handles data reading and processing
├── helpers.py                  # Contains helper functions
├── feasibility_checker.py      # Checks solution feasibility
├── output_results_to_csv.py    # Outputs solutions to CSV format
├── final_test_set/             # Folder containing final test data
└── final_solutions/            # Folder storing generated solutions in CSV format
```

## How to Run

To run the main algorithm, execute:

```
python heuristic_greedy.py
```

This will process the instances in the `final_test_set` folder and generate solutions in the `final_solutions` folder.

## Feasibility Checking

To check the feasibility of generated solutions, run:

```
python feasibility_checker.py ./final_test_set/ ./final_solutions/ > feasibility_checker_solution_output.txt
```

This command will output the feasibility check results to `feasibility_checker_solution_output.txt`.

## Components

- `heuristic_greedy.py`: Implements the main greedy heuristic algorithm for route optimization.
- `assignment_problem.py`: Contains the assignment algorithm used in the heuristic approach.
- `Courier.py`, `Delivery.py`, `Route.py`: Define data classes for couriers, deliveries, and routes.
- `read_data.py`: Handles reading and processing input data from the `final_test_set` folder.
- `helpers.py`: Provides utility functions used throughout the project.
- `feasibility_checker.py`: Checks the feasibility of generated solutions.
- `output_results_to_csv.py`: Converts solutions to the required CSV format.

## Data

- Input data is located in the `final_test_set` folder.
- Generated solutions are stored in the `final_solutions` folder in CSV format.
