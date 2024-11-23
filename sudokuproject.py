# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 23:33:46 2024

@author: Bashayer
"""

import pygame
import sys
import time
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions and constants
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
GRID_SIZE = 540
CELL_SIZE = GRID_SIZE // 9
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Define color palette
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)  # Soft light blue
DARK_BLUE = (70, 130, 180)    # For grid borders
LIGHT_GRAY = (245, 245, 245)  # For the background color of the grid
HIGHLIGHT_COLOR = (255, 204, 0)  # Golden yellow for highlighting cells
RED = (255, 77, 77)  # Soft red for incorrect entries
GREEN = (0, 204, 102)  # Vibrant green for correct entries
BUTTON_COLOR = (70, 130, 180)  # Soft blue for buttons
BUTTON_HOVER_COLOR = (100, 150, 200)  # Lighter blue for hover effect

# Fonts
FONT = pygame.font.SysFont("Poppins", 40)  # Title font
SMALL_FONT = pygame.font.SysFont("Poppins", 20)

# Global variables
selected_cell = None
timer_start = None
difficulty = None
incorrect_cells = set()  # To keep track of incorrect cells

def draw_grid(screen, puzzle, solution, selected_cell):
    """Draw the Sudoku grid, numbers, and highlights."""
    screen.fill(WHITE)  #background for the grid

    # Draw grid lines with soft borders
    for i in range(10):
        line_width = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, DARK_BLUE, (0, i * CELL_SIZE), (GRID_SIZE, i * CELL_SIZE), line_width)
        pygame.draw.line(screen, DARK_BLUE, (i * CELL_SIZE, 0), (i * CELL_SIZE, GRID_SIZE), line_width)

    # Draw numbers with appropriate colors
    for row in range(9):
        for col in range(9):
            num = puzzle[row][col]
            if num is not None:  # Only if num is not None
                if (row, col) in incorrect_cells:
                    color = RED  # Highlight incorrect cells
                elif (row, col) not in incorrect_cells and num == solution[row][col]:
                    color = GREEN  # Highlight correct cells
                else:
                    color = BLACK  # Default color for normal cells
                text = FONT.render(str(abs(num)), True, color)  # Display absolute value for negative entries
                
                screen.blit(text, (col * CELL_SIZE + 20, row * CELL_SIZE + 15))

    # Highlight selected cell with a yellow border
    if selected_cell:
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, (selected_cell[1] * CELL_SIZE, selected_cell[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE), 5)

def draw_background(screen):
    """Draw background."""    
    screen.fill(WHITE)
        
def draw_buttons(screen):
    """Draw the timer, hint, end game, and new game buttons."""
    
    elapsed_time = time.time() - timer_start
    timer_text = SMALL_FONT.render(f"Time: {int(elapsed_time)}s", True, DARK_BLUE)
    screen.blit(timer_text, (10, GRID_SIZE + 10))

    # Draw Hint button with rounded corners and hover effect
    hint_button = pygame.Rect(400, GRID_SIZE + 10, 80, 30)
    pygame.draw.rect(screen, BUTTON_COLOR, hint_button, border_radius=15)  # Rounded corners
    if hint_button.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, hint_button, border_radius=15)
    hint_text = SMALL_FONT.render("Hint", True, WHITE)
    screen.blit(hint_text, (410, GRID_SIZE + 15))
    
    # Draw End Game button with rounded corners and hover effect
    solve_button = pygame.Rect(500, GRID_SIZE + 10 , 80, 30)
    pygame.draw.rect(screen, BUTTON_COLOR, solve_button, border_radius=15)  # Rounded corners
    if solve_button.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, solve_button, border_radius=15)
    solve_text = SMALL_FONT.render("End Game", True, WHITE)
    screen.blit(solve_text, (510, GRID_SIZE + 15))

    return hint_button, solve_button

def draw_difficulty_selection(screen):
    """Draw difficulty selection buttons."""
    
    screen.fill(WHITE)
    title_text = FONT.render("Select Difficulty", True, BLACK)
    screen.blit(title_text, (200, 200))

    difficulties = ["Easy", "Medium", "Hard"]
    buttons = []
    
    for i, diff in enumerate(difficulties):
        button = pygame.Rect(200, 300 + i * 60, 200, 50)
        pygame.draw.rect(screen, GRAY, button)
        text = FONT.render(diff, True, BLACK)
        screen.blit(text, (button.x + 50, button.y + 10))
        buttons.append((button, diff.lower()))

    pygame.display.flip()
    return buttons

def generate_puzzle(difficulty):
    """Generate a Sudoku puzzle based on difficulty."""
    N = 9  # Size of the board
    SRN = int(math.sqrt(N))
    
    # Difficulty map: percentage of elements to remove
    difficulty_map = {"easy": 0.35, "medium": 0.45, "hard": 0.55}
    removal_percentage = difficulty_map[difficulty]
    K = int(N * N * removal_percentage)  # Number of elements to remove
    
    # Initialize empty board
    mat = [[0 for _ in range(N)] for _ in range(N)]
    
    def fill_box(row, col):
        """Fill a 3x3 box with unique numbers."""
        nums = list(range(1, N + 1))
        random.shuffle(nums)
        for i in range(SRN):
            for j in range(SRN):
                mat[row + i][col + j] = nums.pop()

    def un_used_in_box(row_start, col_start, num):
        """Check if a number is unused in a 3x3 box."""
        for i in range(SRN):
            for j in range(SRN):
                if mat[row_start + i][col_start + j] == num:
                    return False
        return True

    def check_if_safe(i, j, num):
        """Check if a number can be placed safely in a cell."""
        return (
            num not in mat[i]  # Check row
            and all(row[j] != num for row in mat)  # Check column
            and un_used_in_box(i - i % SRN, j - j % SRN, num)  # Check box
        )

    def fill_remaining(i, j):
        """Recursively fill the remaining cells of the board."""
        if i == N - 1 and j == N:
            return True
        if j == N:
            i += 1
            j = 0
        if mat[i][j] != 0:
            return fill_remaining(i, j + 1)
        for num in range(1, N + 1):
            if check_if_safe(i, j, num):
                mat[i][j] = num
                if fill_remaining(i, j + 1):
                    return True
                mat[i][j] = 0
        return False

    def remove_k_digits():
        """Remove K digits to create the puzzle."""
        count = K
        while count > 0:
            i = random.randint(0, N - 1)
            j = random.randint(0, N - 1)
            if mat[i][j] != 0:
                mat[i][j] = 0
                count -= 1

    # Step 1: Fill diagonal 3x3 matrices
    for i in range(0, N, SRN):
        fill_box(i, i)

    # Step 2: Fill remaining cells
    fill_remaining(0, 0)

    # Step 3: Save the solution (completed board)
    solved_sudoku = [row[:] for row in mat]

    # Step 4: Remove K digits to create the puzzle
    remove_k_digits()

    # Prepare puzzle and solution in the required format
    puzzle = [[cell if cell != 0 else None for cell in row] for row in mat]
    solution = [[solved_sudoku[i][j] for j in range(N)] for i in range(N)]
    
    return puzzle, solution

def handle_input(puzzle, solution, pos, key):
    """Handle user input to modify the puzzle."""
    row, col = pos
    
    if puzzle[row][col] is None or puzzle[row][col] < 0:  # Allow input for empty or incorrect cells
        if solution[row][col] == int(key):
            puzzle[row][col] = int(key)  # Set correct value
            incorrect_cells.discard((row, col))  # Remove from incorrect set if it was there
        else:
            puzzle[row][col] = -int(key)  # Mark as incorrect (negative for visual indication)
            incorrect_cells.add((row, col))  # Add to incorrect cells

def game_over_screen(screen):
    """Display 'Game Over' screen with a New Game button."""
    
    screen.fill(WHITE)
    game_over_text = FONT.render("Game Over!", True, RED)
    screen.blit(game_over_text, (200, 250))

    new_game_button = pygame.Rect(200, 350, 200, 50)
    pygame.draw.rect(screen, GRAY, new_game_button)
    new_game_text = FONT.render("New Game", True, BLACK)
    screen.blit(new_game_text, (new_game_button.x + 20, new_game_button.y + 10))

    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if new_game_button.collidepoint(event.pos):
                    return True  # Start new game when button is pressed

def main():
    global selected_cell, timer_start, difficulty, incorrect_cells

    while True:  # Keep the game running indefinitely unless the user quits
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sudoku")

        # Step 1: Difficulty selection screen
        difficulty = None
        while not difficulty:
            buttons = draw_difficulty_selection(screen)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    for button, diff in buttons:
                        if button.collidepoint(event.pos):
                            difficulty = diff

        # Step 2: Generate puzzle and initialize game variables
        puzzle, solution = generate_puzzle(difficulty)
        timer_start = time.time()
        incorrect_cells.clear()
        selected_cell = None

        # Step 3: Main game loop
        game_active = True
        while game_active:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if x < GRID_SIZE and y < GRID_SIZE:
                        selected_cell = (y // CELL_SIZE, x // CELL_SIZE)
                if event.type == KEYDOWN and selected_cell:
                    if event.unicode.isdigit() and 1 <= int(event.unicode) <= 9:
                        handle_input(puzzle, solution, selected_cell, event.unicode)


            # Call the background function first to set the background
            draw_background(screen)
            # Draw grid, buttons, and other UI elements
            draw_grid(screen, puzzle, solution, selected_cell)
            hint_button, solve_button = draw_buttons(screen)

            # Check button clicks
            if event.type == MOUSEBUTTONDOWN:
                if hint_button.collidepoint(event.pos):
                    if selected_cell:
                        row, col = selected_cell
                        puzzle[row][col] = solution[row][col]
                        incorrect_cells.discard((row, col))
                if solve_button.collidepoint(event.pos):
                    puzzle = [row[:] for row in solution]
                    break  # Exit to trigger game over screen

            # Check if the game is over (all cells filled correctly)
            if all(puzzle[row][col] == solution[row][col] for row in range(9) for col in range(9)):
                game_active = False  # Break out of game loop

            pygame.display.flip()

        # Step 4: Game over screen
        if game_over_screen(screen):
            continue  # Restart from the difficulty selection screen

if __name__ == "__main__":
    main()
