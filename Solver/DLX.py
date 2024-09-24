# solvers/DLX.py

import time

class CandidateNode:
    def __init__(self, digit, row, col):
        self.digit = digit
        self.row = row
        self.col = col

class Node:
    def __init__(self, candidate_node=None):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = None  # Reference to the column header
        self.candidate = candidate_node

class ColumnNode(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.size = 0  # Number of nodes in this column

class DLX:
    def __init__(self, size):
        self.SIZE = size
        self.header = ColumnNode("header")
        self.columns = []
        self.column_map = {}
        self.solutions = []
        self.solution_stack = []
        self.found_solution = False 

        # Initialize all constraint columns
        self.initialize_columns()

    def initialize_columns(self):
        """Initialize all constraint columns and link them horizontally."""
        # Position constraints: (row, col)
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                name = f"pos_{row},{col}"
                col_node = ColumnNode(name)
                self.link_column(col_node)
                self.column_map[name] = col_node

        # Row constraints: (row, digit)
        for row in range(self.SIZE):
            for digit in range(1, self.SIZE + 1):
                name = f"row_{row},{digit}"
                col_node = ColumnNode(name)
                self.link_column(col_node)
                self.column_map[name] = col_node

        # Column constraints: (col, digit)
        for col in range(self.SIZE):
            for digit in range(1, self.SIZE + 1):
                name = f"col_{col},{digit}"
                col_node = ColumnNode(name)
                self.link_column(col_node)
                self.column_map[name] = col_node

        # Grid constraints: (grid, digit)
        for grid in range(self.SIZE):
            for digit in range(1, self.SIZE + 1):
                name = f"grid_{grid},{digit}"
                col_node = ColumnNode(name)
                self.link_column(col_node)
                self.column_map[name] = col_node

    def link_column(self, col_node):
        """Link a new column node to the header horizontally."""
        last = self.header.left
        last.right = col_node
        col_node.left = last
        col_node.right = self.header
        self.header.left = col_node
        col_node.up = col_node
        col_node.down = col_node

    def get_column(self, name):
        """Retrieve the column node by name."""
        return self.column_map.get(name, None)

    def add_row(self, row_nodes):
        """Add a row of nodes to the DLX matrix and link them horizontally."""
        # Link the nodes horizontally to form a circular doubly-linked list
        for i in range(len(row_nodes)):
            row_nodes[i].right = row_nodes[(i + 1) % len(row_nodes)]
            row_nodes[(i + 1) % len(row_nodes)].left = row_nodes[i]

        # Link the nodes vertically into their respective columns
        for node in row_nodes:
            column = node.column
            if column is None:
                print(f"Error: Column is None for candidate {node.candidate}")
                continue  # Skip adding this node if column is missing
            node.down = column
            node.up = column.up
            column.up.down = node
            column.up = node
            column.size += 1

    def choose_column(self):
        """Choose the column with the smallest size (fewest nodes)."""
        min_size = float('inf')
        chosen_col = None
        current = self.header.right
        while current != self.header:
            if current.size < min_size:
                min_size = current.size
                chosen_col = current
                if min_size == 0:
                    break
            current = current.right
        return chosen_col

    def cover(self, col_node):
        """Cover a column node."""
        col_node.right.left = col_node.left
        col_node.left.right = col_node.right

        current = col_node.down
        while current != col_node:
            node = current.right
            while node != current:
                node.down.up = node.up
                node.up.down = node.down
                node.column.size -= 1
                node = node.right
            current = current.down

    def uncover(self, col_node):
        """Uncover a column node."""
        current = col_node.up
        while current != col_node:
            node = current.left
            while node != current:
                node.column.size += 1
                node.down.up = node
                node.up.down = node
                node = node.left
            current = current.up

        col_node.right.left = col_node
        col_node.left.right = col_node

    def search(self):
        """Recursive search for solutions."""
        if self.header.right == self.header:
            # Found a solution
            solution = []
            for row_node in self.solution_stack:
                candidate = row_node.candidate
                solution.append((candidate.digit, candidate.row, candidate.col))
            self.solutions.append(solution)
            self.found_solution = True
            return

        # Choose the column with the fewest nodes
        column = self.choose_column()
        if column.size == 0:
            return  # No solution exists

        self.cover(column)

        current = column.down
        while current != column:
            self.solution_stack.append(current)
            if self.found_solution:
                return

            # Cover all columns in this row
            node = current.right
            while node != current:
                self.cover(node.column)
                node = node.right

            self.search()

            # Backtrack
            self.solution_stack.pop()
            node = current.left
            while node != current:
                self.uncover(node.column)
                node = node.left

            current = current.down

        self.uncover(column)

    def solve(self):
        """Initiate the DLX algorithm to find all solutions."""
        self.search()
        return self.solutions

class SudokuSolver:
    def __init__(self):
        self.SIZE = 9
        self.SUBGRID_SIZE = 3

    def get_grid_id(self, row, col):
        """Get the grid index based on row and column."""
        return (row // self.SUBGRID_SIZE) * self.SUBGRID_SIZE + (col // self.SUBGRID_SIZE)

    def is_valid_option(self, digit, row, col, grid, rows, cols, grids):
        """Check if placing digit at (row, col) is valid."""
        if digit in rows[row]:
            return False
        if digit in cols[col]:
            return False
        if digit in grids[grid]:
            return False
        return True

    def solve(self, board):
        """Solve the Sudoku puzzle using DLX."""
        # Initialize constraint sets
        rows = [set() for _ in range(self.SIZE)]
        cols = [set() for _ in range(self.SIZE)]
        grids = [set() for _ in range(self.SIZE)]

        # Populate the constraint sets with pre-filled numbers
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                cell = board[row][col]
                if cell != 0:
                    digit = cell
                    rows[row].add(digit)
                    cols[col].add(digit)
                    grid = self.get_grid_id(row, col)
                    grids[grid].add(digit)

        # Initialize DLX
        dlx = DLX(self.SIZE)

        # Add all possible option rows to DLX
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                grid = self.get_grid_id(row, col)
                if board[row][col] == 0:
                    # Empty cell
                    for digit in range(1, 10):
                        if self.is_valid_option(digit, row, col, grid, rows, cols, grids):
                            # Constraint names
                            pos_constraint = f"pos_{row},{col}"
                            row_constraint = f"row_{row},{digit}"
                            col_constraint = f"col_{col},{digit}"
                            grid_constraint = f"grid_{grid},{digit}"

                            # Retrieve column nodes
                            pos_col = dlx.get_column(pos_constraint)
                            row_col = dlx.get_column(row_constraint)
                            col_col = dlx.get_column(col_constraint)
                            grid_col = dlx.get_column(grid_constraint)

                            # Check if columns exist
                            if not all([pos_col, row_col, col_col, grid_col]):
                                print(f"Error: Missing column(s) for constraints: {pos_constraint}, {row_constraint}, {col_constraint}, {grid_constraint}")
                                continue

                            # Create candidate node
                            candidate = CandidateNode(digit, row, col)

                            # Create nodes for each constraint
                            pos_node = Node(candidate)
                            row_node = Node(candidate)
                            col_node = Node(candidate)
                            grid_node = Node(candidate)

                            # Assign column headers to nodes
                            pos_node.column = pos_col
                            row_node.column = row_col
                            col_node.column = col_col
                            grid_node.column = grid_col

                            # Add the row to DLX
                            dlx.add_row([pos_node, row_node, col_node, grid_node])
                else:
                    # Pre-filled cell: only one possible digit, add its row
                    digit = board[row][col]
                    # Constraint names
                    pos_constraint = f"pos_{row},{col}"
                    row_constraint = f"row_{row},{digit}"
                    col_constraint = f"col_{col},{digit}"
                    grid_constraint = f"grid_{grid},{digit}"

                    # Retrieve column nodes
                    pos_col = dlx.get_column(pos_constraint)
                    row_col = dlx.get_column(row_constraint)
                    col_col = dlx.get_column(col_constraint)
                    grid_col = dlx.get_column(grid_constraint)

                    # Check if columns exist
                    if not all([pos_col, row_col, col_col, grid_col]):
                        print(f"Error: Missing column(s) for constraints: {pos_constraint}, {row_constraint}, {col_constraint}, {grid_constraint}")
                        continue

                    candidate = CandidateNode(digit, row, col)

                    # Create nodes for each constraint
                    pos_node = Node(candidate)
                    row_node = Node(candidate)
                    col_node = Node(candidate)
                    grid_node = Node(candidate)

                    # Assign column headers to nodes
                    pos_node.column = pos_col
                    row_node.column = row_col
                    col_node.column = col_col
                    grid_node.column = grid_col

                    # Add the row to DLX
                    dlx.add_row([pos_node, row_node, col_node, grid_node])

        # Solve using DLX
        start_time = time.perf_counter()
        solutions = dlx.solve()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        # Format solutions
        formatted_solutions = []
        for solution in solutions:
            solved_board = [[0 for _ in range(self.SIZE)] for _ in range(self.SIZE)]
            for digit, row, col in solution:
                solved_board[row][col] = digit
            formatted_solutions.append(solved_board)

        if formatted_solutions:
            return {
                "found_solutions": formatted_solutions,
                "time_elapsed": f"{elapsed_time:.5f} seconds"
            }
        else:
            return {
                "found_solutions": [],
                "time_elapsed": f"{elapsed_time:.5f} seconds"
            }




