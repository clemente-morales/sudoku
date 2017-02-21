rows = 'ABCDEFGHI'
cols = '123456789'

assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# ['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9']
upper_left_to_right_bottom = [row+col for (row, col) in zip(rows, cols)]

# ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']
upper_right_to_left_bottom = [row+col for (row, col) in zip(rows, cols[::-1])] 

unitlist = row_units + column_units + square_units

unitlist_with_x = row_units + column_units + square_units + upper_left_to_right_bottom + upper_right_to_left_bottom

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

# complete units with upper_left_to_right_bottom
for k, v in units.items():
    if k in upper_left_to_right_bottom:
        units[k].append(upper_left_to_right_bottom)
    elif k in upper_right_to_left_bottom:
        units[k].append(upper_right_to_left_bottom)

peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def count_boxes_solved(values): 
    return len([box for box in values.keys() if len(values[box]) == 1])

def get_unfilled_squares(values): 
    return [box for box in values.keys() if len(values[box]) > 1]

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(solution):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    solution = apply_naked(column_units, solution)
    return apply_naked(row_units, solution)

def apply_naked(units, solution):
    for unit in units:
        # Find all instances of naked twins
        unit_values = list(map(lambda box: solution[box], unit))
        naked_twins = [(box, solution[box]) for box in unit if len(solution[box]) == 2 and unit_values.count(solution[box])==2]
        
        # Eliminate the naked twins as possibilities
        for twin, twin_value in naked_twins:
            peer_keys = peers[twin]
            for peer_key in unit:
                if (solution[peer_key] != twin_value and len(solution[peer_key]) > 1): 
                    solution[peer_key] = "".join(filter(lambda char: char not in twin_value, solution[peer_key]))
                    
    return solution

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    sudoku = dict(zip(boxes, grid))
    
    for k, v in sudoku.items():
        if v == '.' :
            sudoku[k] = '123456789'
    
    return sudoku

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solution = values.copy()
    for k, v in values.items():
        if len(v) == 1 :
            peer_keys = peers[k]

            for peer_key in peer_keys:
                solution[peer_key] = "".join(filter(lambda char: char != v, solution[peer_key]))
    
    
    return solution 

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        validValues = '123456789'
        for digit in validValues:
            ocurrences = list(filter(lambda peer : digit in values[peer], unit))
            if len(ocurrences) == 1:
                values[ocurrences[0]] = digit
    
    return values

def reduce_puzzle(values):
    """Apply constrains to narrow the possibilities of the answer.

    Apply Elimination and only choice technique to narrow the answer.  

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after after applying the constrains.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = count_boxes_solved(values)

        # Apply constrains
        values = eliminate(values) 
        values = only_choice(values)
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = count_boxes_solved(values)
        
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """Using depth-first search and propagation, create a search tree and solve the sudoku.  

    Input: Sudoku in dictionary form.
    Output: Solution for the Sudoku.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    
    if values is False:
        return False
    
    if count_boxes_solved(values) == 81:
        return values
    
    # Choose one of the unfilled squares with the fewest possibilities
    unfilled_boxes = get_unfilled_squares(values)
    unfilled_boxes.sort(key = lambda s: len(values[s]))
    box_to_attempt_key = unfilled_boxes[0]
    box_to_attempt_value = values[box_to_attempt_key] 
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for possible_value in box_to_attempt_value:
        potential_solution = values.copy()
        potential_solution[box_to_attempt_key] = possible_value
        potential_solution = search(potential_solution)
        if (potential_solution):
            return potential_solution

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))
    
if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
