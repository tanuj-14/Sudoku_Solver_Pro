import time
import copy

def is_valid(grid, row, col, num):
    """
    Check if it's valid to place the number in the cell (row, col).
    """
    # Check the row
    for i in range(9):
        if grid[row][i] == num:
            return False

    # Check the column
    for i in range(9):
        if grid[i][col] == num:
            return False

    # Check the 3x3 subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[start_row + i][start_col + j] == num:
                return False

    return True

def find_empty(grid):
    """
    Find an empty cell in the grid (represented by 0).
    Returns a tuple (row, col) if found, otherwise None.
    """
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return row, col
    return None

def solve_backtracking(grid):
    """
    Solves the Sudoku using backtracking.
    Returns the solved grid if solvable, otherwise None.
    """
    empty = find_empty(grid)
    if not empty:
        return grid  # No empty spaces, puzzle solved
    row, col = empty

    for num in range(1, 10):  # Try numbers 1 through 9
        if is_valid(grid, row, col, num):
            grid[row][col] = num

            if solve_backtracking(grid):
                return grid

            # If placing the number didn't lead to a solution, backtrack
            grid[row][col] = 0

    return None

def backTrackingSolver(grid):
    """
    Solves the Sudoku using backtracking and measures the time taken.
    Returns the solved grid or None.
    """
    # Create a deep copy of the grid to avoid modifying the original
    grid_copy = copy.deepcopy(grid)

    start_time = time.perf_counter()  # Start the timer

    solved_grid = solve_backtracking(grid_copy)

    end_time = time.perf_counter()  # Stop the timer
    elapsed_time = end_time - start_time

    # Print the time taken (optional)
    print(f"Backtracking Solver: {elapsed_time:.5f} seconds")

    return solved_grid ,elapsed_time # Return the solved grid or None
