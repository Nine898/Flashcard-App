from tkinter import filedialog, messagebox
import pygame
import random
import sys
import time
import os
import colorsys
import json

pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 800, 600  # Window dimensions
FPS = 180  # Frames per second

# Color presets (RGB format)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREEN  = (0, 200, 0)
RED    = (200, 0, 0)
BLUE   = (50, 50, 255)
GRAY   = (200, 200, 200)

# Font settings
FONT = pygame.font.Font(None, 36)  # Standard font
BIG_FONT = pygame.font.Font(None, 48)  # Larger font for emphasis

def show_feedback(message, duration=1500, color=RED, y_offset=0):
    """Display feedback message on screen for a short duration."""
    screen.fill(WHITE)  # Clear the screen
    text = FONT.render(message, True, color)  # Render text
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))  # Center text
    screen.blit(text, text_rect)  # Display message
    pygame.display.flip()  # Update screen
    pygame.time.wait(duration)  # Pause for specified duration

def create_button(text, x, y, width, height, color=GRAY):
    """Create a button with given parameters."""
    button = pygame.Rect(x, y, width, height)  # Define button rectangle
    return {"rect": button, "text": text, "color": color}  # Return button properties

def draw_button_list(buttons):
    """Render a list of buttons on the screen."""
    for button in buttons:
        draw_button(button["text"], button["rect"], button["color"])  # Draw each button

def handle_button_click(button_rect, flashcards, action_fn, empty_message="Please enter flashcards first!"):
    """Execute action on button click, ensuring flashcards exist if required."""
    if flashcards or action_fn == enter_flashcards:  # Check if flashcards exist
        return action_fn(flashcards) if flashcards else action_fn()  # Execute function
    else:
        show_feedback(empty_message)  # Show error message
    return flashcards  # Return current flashcards list

def create_text_surface(text, font=FONT, color=BLACK, centered=True):
    """Create a text surface for rendering."""
    text_surface = font.render(text, True, color)  # Render text
    return text_surface, text_surface.get_rect(center=(WIDTH//2, HEIGHT//2)) if centered else text_surface  # Return position

def get_wrapped_text_height(text, font, max_width):
    """Calculate the height needed for wrapped text."""
    return len(wrap_text(text, font, max_width)) * font.get_height()  # Determine text height

def render_wrapped_text(text, font, max_width, start_x, start_y, color=BLACK, centered=False):
    """Render multi-line text while respecting max width constraints."""
    lines = wrap_text(text, font, max_width)  # Split text into lines
    total_height = 0  # Track total rendered height
    for line in lines:
        text_surface = font.render(line, True, color)  # Render line
        x = start_x + (max_width - text_surface.get_width()) // 2 if centered else start_x  # Align text
        screen.blit(text_surface, (x, start_y + total_height))  # Display line
        total_height += font.get_height()  # Update height
    return total_height  # Return final height

def handle_scroll(current_offset, max_scroll, event):
    """Modify scroll position based on mouse wheel or arrow key input."""
    if event.type == pygame.MOUSEWHEEL:  # Mouse scroll event
        return max(0, min(current_offset - event.y * 10, max_scroll))  # Adjust scroll position
    elif event.type == pygame.KEYDOWN:  # Keyboard event
        if event.key == pygame.K_UP:
            return max(0, current_offset - 10)  # Scroll up
        elif event.key == pygame.K_DOWN:
            return min(current_offset + 10, max_scroll)  # Scroll down
    return current_offset  # Return updated scroll offset

def check_quit_event(event):
    """Exit the program if the quit event is triggered."""
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

def center_rect(width, height, y_offset=0):
    """Generate a rectangle centered on the screen."""
    return pygame.Rect((WIDTH - width) // 2, (HEIGHT - height) // 2 + y_offset, width, height)

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flashcard App")  # Window title
clock = pygame.time.Clock()  # Frame timing

class Flashcard:
    """Represents a flashcard with a front and back side."""
    def __init__(self, front, back):
        self.front = front  # Front text
        self.back = back  # Back text
        self.showing_front = True  # Track current side
    
    def flip(self):
        """Flip the flashcard to reveal the other side."""
        self.showing_front = not self.showing_front

# Text rendering utilities
def get_wrapped_lines(text, font, max_width):
    """Break text into lines that fit within the given width."""
    words = text.split()  # Split text into words
    lines, current_line = [], ""
    for word in words:
        test_line = f"{current_line} {word}".strip()  # Simulate adding a word
        if font.size(test_line)[0] <= max_width - 20:  # Ensure it fits within margin
            current_line = test_line  # Update current line
        else:
            lines.append(current_line)  # Store full line
            current_line = word  # Start new line
    if current_line:
        lines.append(current_line)  # Add last line
    return lines  # Return processed lines

def calculate_text_dimensions(lines, font):
    """Calculate the total height of multi-line text."""
    return font.get_height(), len(lines) * font.get_height()

def draw_text_in_box(text, rect, font, color, scroll_offset=0, target_surface=screen):
    """Render wrapped text within a defined box."""
    x, y, width, height = rect
    lines = get_wrapped_lines(text, font, width)  # Get text lines
    line_height, total_text_height = calculate_text_dimensions(lines, font)  # Determine dimensions

    # Adjust start position based on text height
    start_y = y + (height - total_text_height) // 2 - scroll_offset if total_text_height < height else y - scroll_offset

    for line in lines:
        rendered_line = font.render(line, True, color)  # Render text line
        target_surface.blit(rendered_line, (x + (width - rendered_line.get_width()) // 2, start_y))  # Center text
        start_y += line_height  # Move to next line

def draw_flashcard(card, pos=(100, 200), size=(600, 200), scroll_offset=0):
    """Draw a flashcard at the specified position."""
    x, y = pos
    w, h = size
    bg_color = getattr(card, "color", (0, 0, 0))  # Get card's background color
    pygame.draw.rect(screen, bg_color, (x, y, w, h))  # Draw card rectangle
    text = card.front if card.showing_front else card.back  # Display front or back text
    draw_text_in_box(text, (x, y, w, h), FONT, WHITE, scroll_offset)  # Render text

def create_centered_rect(width, height, y_offset=0):
    """Generate a centered rectangle on the screen."""
    return pygame.Rect((WIDTH - width) // 2, (HEIGHT - height) // 2 + y_offset, width, height)

def create_button_pair(y_pos, width=200, height=50, spacing=200):
    """Create two buttons with spacing, positioned at y_pos."""
    left_rect = pygame.Rect((WIDTH - width * 2 - spacing) // 2, y_pos, width, height)
    right_rect = pygame.Rect(left_rect.right + spacing, y_pos, width, height)
    return left_rect, right_rect

def draw_button(text, rect, color=GRAY):
    """Render a button with text."""
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, WHITE, rect, 3)  # Outline
    text_rendered = FONT.render(text, True, BLACK)  # Render button text
    text_rect = text_rendered.get_rect(center=rect.center)  # Center text
    screen.blit(text_rendered, text_rect)  # Draw text on button

def render_flashcard_surface(card, size=(600, 200)):
    """Create a separate surface for flashcard rendering."""
    surface = pygame.Surface(size, pygame.SRCALPHA)  # Transparent background
    bg_color = getattr(card, "color", (0, 0, 0))  # Get flashcard color
    surface.fill(bg_color)  # Fill surface with color
    text = card.front if card.showing_front else card.back  # Get flashcard text
    draw_text_in_box(text, (0, 0, size[0], size[1]), FONT, WHITE, 0, target_surface=surface)  # Render text
    return surface

def wrap_text(text, font, max_width):
    """Splits text into lines that fit within the max width."""
    words = text.split(' ')  # Split text into words
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "  # Simulate adding the word
        width, _ = font.size(test_line)  # Check the rendered width
        if width > max_width and current_line != "":  # If too wide, start new line
            lines.append(current_line)
            current_line = word + " "
        else:
            current_line = test_line
    lines.append(current_line)  # Add the final line
    return lines


# Input handling utilities
def handle_text_input(event, current_text, cursor_pos):
    """Handles text input events such as typing, deleting, and moving cursor."""
    if event.key == pygame.K_BACKSPACE and cursor_pos > 0:
        return current_text[:cursor_pos-1] + current_text[cursor_pos:], cursor_pos - 1
    elif event.key == pygame.K_DELETE and cursor_pos < len(current_text):
        return current_text[:cursor_pos] + current_text[cursor_pos+1:], cursor_pos
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        return None, None  # Finish input
    elif event.key == pygame.K_LEFT:
        return current_text, max(0, cursor_pos - 1)  # Move cursor left
    elif event.key == pygame.K_RIGHT:
        return current_text, min(len(current_text), cursor_pos + 1)  # Move cursor right
    elif event.key == pygame.K_HOME:
        return current_text, 0  # Move cursor to start
    elif event.key == pygame.K_END:
        return current_text, len(current_text)  # Move cursor to end
    else:
        return current_text[:cursor_pos] + event.unicode + current_text[cursor_pos:], cursor_pos + len(event.unicode)


def get_text_input(prompt):
    """Handles user input for text fields with blinking cursor effect."""
    input_text = ""
    cursor_pos = 0
    active = True
    blink_timer = 0
    show_cursor = True

    while active:
        screen.fill(WHITE)  # Clear screen
        prompt_surface = FONT.render(prompt, True, BLACK)
        prompt_x = (WIDTH - prompt_surface.get_width()) // 2
        prompt_y = (HEIGHT - prompt_surface.get_height()) // 2 - 50
        screen.blit(prompt_surface, (prompt_x, prompt_y))

        # Create input box
        input_rect = pygame.Rect((WIDTH - 700) // 2, prompt_y + prompt_surface.get_height() + 20, 700, 150)
        pygame.draw.rect(screen, GRAY, input_rect)  # Background
        pygame.draw.rect(screen, BLACK, input_rect, 2)  # Border

        # Wrap text at cursor position
        full_text_wrapped = wrap_text(input_text, FONT, input_rect.width - 20)

        # Draw text and cursor
        y_offset = input_rect.top + 5
        current_pos = 0
        cursor_x, cursor_y = input_rect.left + 10, y_offset

        for line in full_text_wrapped:
            line_surf = FONT.render(line, True, BLACK)
            screen.blit(line_surf, (input_rect.left + 10, y_offset))

            # Find cursor position within wrapped text
            if current_pos + len(line) >= cursor_pos and current_pos <= cursor_pos:
                cursor_x = input_rect.left + 10 + FONT.size(line[:cursor_pos - current_pos])[0]
                cursor_y = y_offset

            current_pos += len(line)
            y_offset += FONT.get_height()

        # Blink cursor effect
        blink_timer += 1
        if blink_timer >= FPS // 2:
            show_cursor = not show_cursor
            blink_timer = 0
        if show_cursor:
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + FONT.get_height()), 2)

        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                    break
                input_text, cursor_pos = handle_text_input(event, input_text, cursor_pos)
                show_cursor = True
                blink_timer = 0

        clock.tick(FPS)

    return input_text


def get_answer_input(question):
    """Displays a question and captures user input as an answer."""
    input_text = ""
    active = True
    while active:
        screen.fill(WHITE)
        question_surface = BIG_FONT.render(question, True, BLACK)
        qs_rect = question_surface.get_rect(center=(WIDTH // 2, 150))
        screen.blit(question_surface, qs_rect.topleft)

        # Answer label
        answer_label = FONT.render("Answer:", True, BLACK)
        screen.blit(answer_label, (50, 300))

        # Input field
        input_rect = pygame.Rect(150, 290, 500, 50)
        pygame.draw.rect(screen, GRAY, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)

        # Render input text
        input_surface = FONT.render(input_text, True, BLACK)
        screen.blit(input_surface, (input_rect.x + 10, input_rect.y + 10))
        pygame.display.flip()

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                    break
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]  # Remove last character
                else:
                    input_text += event.unicode  # Add new character

        clock.tick(FPS)

    return input_text


# Flashcard storage
FLASHCARD_FILE = "flashcards.json"

def save_flashcards(flashcards):
    """Saves flashcards to a JSON file."""
    data = [{"front": card.front, "back": card.back} for card in flashcards]
    with open(FLASHCARD_FILE, "w") as f:
        json.dump(data, f)

def load_flashcards():
    """Loads flashcards from a JSON file, handling errors."""
    try:
        with open(FLASHCARD_FILE, "r") as f:
            data = json.load(f)
        return [Flashcard(item["front"], item["back"]) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def enter_flashcards():
    """Displays stored flashcards and allows adding/removing."""
    flashcards = load_flashcards()
    scroll_offset = 0
    max_scroll = max(0, (len(flashcards) * 30) - (HEIGHT - 250))  # Calculate max scroll
    scroll_speed = 30  
    running = True

    while running:
        screen.fill(WHITE)  # Clear the screen

        # Display header text
        header = FONT.render("Flashcards Entered:", True, BLACK)
        screen.blit(header, (50, 30 - scroll_offset))

        # Render flashcards with wrapping
        for i, card in enumerate(flashcards):
            card_text = f"{i+1}. {card.front} → {card.back}"
            wrapped_text = wrap_text(card_text, FONT, WIDTH - 100)
            y_pos = 60 + i * 30 - scroll_offset

            for line in wrapped_text:
                card_surface = FONT.render(line, True, BLACK)
                screen.blit(card_surface, (50, y_pos))
                y_pos += FONT.get_height()

        # Button setup for adding/removing flashcards
        button_width, button_height = 250, 80
        dynamic_button_y = 120 + (len(flashcards) * 40)  # Adjust button position dynamically
        add_button = pygame.Rect((WIDTH // 2) - (button_width + 20), dynamic_button_y, button_width, button_height)
        remove_button = pygame.Rect((WIDTH // 2) + 10, dynamic_button_y, button_width, button_height)
        exit_button = pygame.Rect((WIDTH // 2) - (button_width // 2), dynamic_button_y + 100, button_width, button_height) 

        # Draw buttons
        pygame.draw.rect(screen, GREEN, add_button)
        pygame.draw.rect(screen, RED, remove_button)
        pygame.draw.rect(screen, GRAY, exit_button)

        # Display button labels
        screen.blit(FONT.render("Add Flashcard", True, WHITE), add_button.topleft)
        screen.blit(FONT.render("Remove Flashcard", True, WHITE), remove_button.topleft)
        screen.blit(FONT.render("Return", True, WHITE), exit_button.topleft)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Handle button clicks
                x, y = event.pos
                if add_button.collidepoint(x, y):
                    front = get_text_input("Enter flashcard FRONT:")
                    back = get_text_input("Enter flashcard BACK:")
                    flashcards.append(Flashcard(front, back))  # Add new flashcard
                    save_flashcards(flashcards)
                elif remove_button.collidepoint(x, y) and flashcards:
                    index_str = get_text_input("Enter flashcard numbers to remove:")
                    try:
                        indices = [int(i.strip()) - 1 for i in index_str.split(',')]  # Get selected flashcards
                        for i in sorted(indices, reverse=True):
                            del flashcards[i]  # Remove selected flashcards
                            save_flashcards(flashcards)
                            show_feedback("Flashcards removed!", color=GREEN)
                    except ValueError:
                        show_feedback("Invalid input, use comma-separated numbers.", color=RED)
                elif exit_button.collidepoint(x, y):
                    running = False  
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 10)  # Scroll up
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(scroll_offset + 10, max_scroll)  # Scroll down
    return flashcards


def animate_shuffle(flashcards):
    """Applies a shuffled animation effect to flashcards."""
    import random
    if not flashcards:
        return flashcards

    existing_colors = set()
    for card in flashcards:
        while True:
            r, g, b = random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)
            if g > 130 and r > 130 and b < 100:  # Avoid excessive brightness
                continue
            new_color = (r, g, b)
            if new_color not in existing_colors:
                existing_colors.add(new_color)
                card.color = new_color
                break

    scatter_duration, converge_duration = 1.2, 1.2
    base_x, base_y = 100, 200
    num_cards = len(flashcards)
    initial_positions = [(base_x + i * 3, base_y + i * 3) for i in range(num_cards)]
    
    # Scatter random positions and rotations
    scatter_positions = [(x + random.randint(-200, 200), y + random.randint(-150, 150)) for x, y in initial_positions]
    scatter_rotations = [random.randint(-90, 90) for _ in range(num_cards)]
    front_card = flashcards[0]

    def lerp(a, b, t): return a + (b - a) * t
    def lerp_tuple(a, b, t): return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))

    # Scatter animation phase
    scatter_start = time.time()
    while time.time() - scatter_start < scatter_duration:
        t_frac = (time.time() - scatter_start) / scatter_duration
        screen.fill(WHITE)
        for i, card in enumerate(flashcards):
            cur_pos = lerp_tuple(initial_positions[i], scatter_positions[i], t_frac)
            cur_rot = lerp(0, scatter_rotations[i], t_frac)
            if card == front_card:
                cur_rot += 90 * t_frac
            card_surface = render_flashcard_surface(card)
            rotated_surface = pygame.transform.rotate(card_surface, cur_rot)
            rect = rotated_surface.get_rect(center=(cur_pos[0] + 300, cur_pos[1] + 100))
            screen.blit(rotated_surface, rect.topleft)
        pygame.display.flip()
        clock.tick(FPS)

    # Shuffle order
    random.shuffle(flashcards)
    final_positions = {card: (base_x + i * 3, base_y + i * 3) for i, card in enumerate(flashcards)}

    # Converge animation phase
    converge_start = time.time()
    while time.time() - converge_start < converge_duration:
        t_frac = (time.time() - converge_start) / converge_duration
        screen.fill(WHITE)
        for i, card in enumerate(flashcards):
            start_pos = scatter_positions[i]
            final_pos = final_positions[card]
            cur_pos = lerp_tuple(start_pos, final_pos, t_frac)
            cur_rot = lerp(scatter_rotations[i], 0, t_frac)
            if card == front_card:
                cur_rot += 90 * (1 - t_frac)
            card_surface = render_flashcard_surface(card)
            rotated_surface = pygame.transform.rotate(card_surface, cur_rot)
            rect = rotated_surface.get_rect(center=(cur_pos[0] + 300, cur_pos[1] + 100))
            screen.blit(rotated_surface, rect.topleft)
        pygame.display.flip()
        clock.tick(FPS)
        flashcards[:] = new_order
    return flashcards


def animate_reverse(flashcards):
    """Animates flipping flashcards in reverse with a color transition."""
    
    def rotate_color(color, factor):
        """Rotates the hue of a color to create a smooth transition effect."""
        r, g, b = color
        r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
        h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        h_new = (h + 0.5 * factor) % 1.0  # Adjust hue
        r_new, g_new, b_new = colorsys.hsv_to_rgb(h_new, s, v)
        return (int(r_new * 255), int(g_new * 255), int(b_new * 255))

    num_steps = 15  # Number of animation steps
    for card in flashcards:
        original_color = getattr(card, "color", (0, 0, 0))  # Store initial color
        for i in range(num_steps):
            screen.fill(WHITE)  # Clear screen
            squeeze_factor = abs((i - num_steps / 2) / (num_steps / 2))  # Squash effect
            new_width = max(1, int(600 * squeeze_factor))  # Adjust width dynamically
            x = 100 + (600 - new_width) // 2  # Centering effect
            t = i / (num_steps - 1)  # Normalized time factor
            rotated_bg = rotate_color(original_color, t)  # Apply color transition

            temp_surface = pygame.Surface((new_width, 200))  # Create card surface
            temp_surface.fill(rotated_bg)  # Apply color
            text = card.front if i < num_steps / 2 else card.back  # Determine displayed text

            draw_text_in_box(text, (0, 0, new_width, 200), FONT, WHITE, 0, target_surface=temp_surface)
            screen.blit(temp_surface, (x, 200))  # Display the animated card
            pygame.display.flip()
            clock.tick(30)  # Control animation speed
        card.flip()
        card.color = rotate_color(original_color, 1)  # Final color adjustment
    
    return flashcards


def animate_flip(card):
    """Animates a card flipping with a squeeze effect."""
    num_steps = 15
    card_pos = (100, 200)
    card_size = (600, 200)

    for i in range(num_steps):
        screen.fill(WHITE)
        instruction = "Track Progress: SPACE to flip"
        instr_surface = FONT.render(instruction, True, BLACK)
        screen.blit(instr_surface, (WIDTH // 2 - instr_surface.get_width() // 2, 30))

        factor = abs((i - num_steps / 2) / (num_steps / 2))  # Squash effect
        new_width = max(1, int(card_size[0] * factor))  # Adjust width
        x = card_pos[0] + (card_size[0] - new_width) // 2  # Centering effect

        temp_surface = pygame.Surface((new_width, card_size[1]))  # Create surface
        temp_surface.fill(getattr(card, "color", (0, 0, 0)))  # Use card color
        pygame.draw.rect(temp_surface, WHITE, (0, 0, new_width, card_size[1]), 3)  # Border

        text = card.front if i < num_steps / 2 else card.back  # Determine text side
        draw_text_in_box(text, (0, 0, new_width, card_size[1]), FONT, WHITE, 0, target_surface=temp_surface)

        screen.blit(temp_surface, (x, card_pos[1]))  # Display card
        pygame.display.flip()
        pygame.time.wait(30)  # Control flip animation speed

    card.flip()  # Flip the card at the end


def track_progress_mode(flashcards):
    """Allows user to track progress of known/unknown flashcards."""
    known_cards = []
    unknown_cards = []
    index = 0
    scroll_offset = 0
    total_cards = len(flashcards)

    # Assign random colors to flashcards
    for card in flashcards:
        if not hasattr(card, "color") or card.color == (0, 0, 0):
            card.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    while index < total_cards:
        screen.fill(WHITE)

        instruction = "Track Progress: SPACE to flip"
        instr_surface = FONT.render(instruction, True, BLACK)
        screen.blit(instr_surface, (WIDTH // 2 - instr_surface.get_width() // 2, 30))

        draw_flashcard(flashcards[index], scroll_offset=scroll_offset)  # Display current flashcard

        # Create buttons for known/unknown categorization
        known_rect = pygame.Rect(100, 450, 200, 50)
        unknown_rect = pygame.Rect(500, 450, 200, 50)
        draw_button("Known", known_rect, GREEN)
        draw_button("Unknown", unknown_rect, RED)
        pygame.display.flip()

        decision_made = False  # Track decision state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, scroll_offset - event.y * 10)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 10)  # Scroll up
                elif event.key == pygame.K_DOWN:
                    scroll_offset += 10  # Scroll down
                elif event.key == pygame.K_SPACE:
                    animate_flip(flashcards[index])  # Flip flashcard
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:  # Categorization
                    flashcards[index].color = GREEN if event.key == pygame.K_LEFT else RED
                    (known_cards if event.key == pygame.K_LEFT else unknown_cards).append(flashcards[index])
                    index += 1
                    scroll_offset = 0
                    decision_made = True
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Handle button clicks
                x, y = event.pos
                if known_rect.collidepoint(x, y):
                    flashcards[index].color = GREEN
                    known_cards.append(flashcards[index])
                    index += 1
                    scroll_offset = 0
                    decision_made = True
                elif unknown_rect.collidepoint(x, y):
                    flashcards[index].color = RED
                    unknown_cards.append(flashcards[index])
                    index += 1
                    scroll_offset = 0
                    decision_made = True

        if decision_made:
            pygame.time.wait(200)  # Short delay after selection
        clock.tick(FPS)

    # Summary screen
    screen.fill(WHITE)
    summary_text = f"Review complete! Known: {len(known_cards)} | Unknown: {len(unknown_cards)}"
    summary_surface = BIG_FONT.render(summary_text, True, BLACK)
    screen.blit(summary_surface, (WIDTH // 2 - summary_surface.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(2000)

    # Retry unknown flashcards if needed
    if unknown_cards:
        retry = None
        while retry is None:
            screen.fill(WHITE)
            prompt_surface = FONT.render("Retry unknown flashcards? (Y/N)", True, BLACK)
            screen.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    retry = event.key == pygame.K_y if event.key in [pygame.K_y, pygame.K_n] else None

        if retry:
            track_progress_mode(unknown_cards)

    return known_cards, unknown_cards

def test_yourself_mode(flashcards):
    """Allows users to test themselves on flashcards by typing answers."""
    if not flashcards:
        return

    num_cards = None
    while num_cards is None or num_cards > len(flashcards) or num_cards <= 0:  
        screen.fill(WHITE)

        # Display error messages for invalid inputs
        if num_cards is not None:
            if num_cards > len(flashcards):
                show_feedback(f"Please choose a number between 1 and {len(flashcards)}")
            elif num_cards <= 0:
                show_feedback("Please enter a positive number")

        num_str = get_text_input("Enter the number of flashcards to test:")
        try:
            num_cards = int(num_str)
            if num_cards > len(flashcards):
                num_cards = None  # Reset so the user is prompted again
        except ValueError:
            show_feedback("Please input a valid number.", color=RED)

    test_cards = random.sample(flashcards, num_cards)  # Select flashcards randomly
    score = 0

    for card in test_cards:
        card.showing_front = True  # Display the front of the card
        screen.fill(WHITE)

        # Display the question
        question = f"What is the back of this flashcard: {card.front}?"
        wrapped_question = wrap_text(question, FONT, WIDTH - 100)
        y_start = 100  
        for i, line in enumerate(wrapped_question):
            line_surf = FONT.render(line, True, BLACK)
            x = (WIDTH - line_surf.get_width()) // 2
            screen.blit(line_surf, (x, y_start + i * FONT.get_height()))

        # Input field setup
        input_rect = pygame.Rect(50, HEIGHT - 245, WIDTH - 100, 100)
        pygame.draw.rect(screen, GRAY, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)
        pygame.display.flip()

        # Capture user input
        answer = get_text_input("Your Answer:")

        # Check if answer is correct
        if answer.strip().lower() == card.back.strip().lower():
            score += 1
        else:
            screen.fill(WHITE)
            correct_text = f"Correct Answer: {card.back}"
            wrapped_correct = wrap_text(correct_text, BIG_FONT, WIDTH - 100)
            y_start = (HEIGHT - len(wrapped_correct) * BIG_FONT.get_height()) // 2
            for line in wrapped_correct:
                line_surf = BIG_FONT.render(line, True, BLACK)
                x = (WIDTH - line_surf.get_width()) // 2
                screen.blit(line_surf, (x, y_start))
                y_start += BIG_FONT.get_height()
            pygame.display.flip()
            pygame.time.wait(1500)

    # Display final score
    screen.fill(WHITE)
    result_surface = BIG_FONT.render(f"You scored {score} out of {num_cards}", True, BLACK)
    screen.blit(result_surface, ((WIDTH - result_surface.get_width()) // 2,
                                  (HEIGHT - result_surface.get_height()) // 2))
    pygame.display.flip()
    pygame.time.wait(3000)


def display_flashcards_text(flashcards):
    """Displays flashcards as text for review with simple selection."""
    items = [f"Front: {card.front}\nBack: {card.back}" for card in flashcards]
    
    # Print flashcards to console (for debugging purposes)
    for item in items:
        print(f"{item}\n")

    scroll_offset = 0
    active = True
    selection_start = selection_end = 0

    while active:
        screen.fill(WHITE)
        title = BIG_FONT.render("Flashcards Text - Press any key to return", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        text_surface = FONT.render(content, True, BLACK)
        text_rect = text_surface.get_rect(topleft=(50, 100))

        # Draw selection highlight
        if selection_start != selection_end:
            selection_rect = pygame.Rect(text_rect.left + FONT.size(content[:selection_start])[0],
                                         text_rect.top + FONT.get_height() * (selection_start // 70),
                                         FONT.size(content[selection_start:selection_end])[0],
                                         FONT.get_height() * ((selection_end - selection_start) // 70 + 1))
            pygame.draw.rect(screen, (100, 100, 255), selection_rect, 2)

        draw_text_in_box(content, (50, 100, 700, 450), FONT, BLACK, scroll_offset)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                active = False  # Exit screen on key press
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset += -event.y * 10  # Scroll up/down
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Selection handling
                x, y = event.pos
                char_index = (y - text_rect.top) // FONT.get_height() * 70 + (x - text_rect.left) // FONT.size(" ")[0]
                if char_index < len(content):
                    if event.button == 1:  
                        selection_start = selection_end = char_index  # Start selection
                    elif event.button == 3:  
                        selected_text = content[selection_start:selection_end]  # Copy selected text
                        screen.blit(FONT.render(selected_text, True, BLACK), (100, 500))
                        pygame.display.flip()
                        pygame.time.wait(500)
                        selection_start = selection_end = 0  # Reset selection
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  
                    x, y = event.pos
                    char_index = (y - text_rect.top) // FONT.get_height() * 70 + (x - text_rect.left) // FONT.size(" ")[0]
                    if char_index < len(content):
                        selection_end = char_index  # Extend selection

        clock.tick(FPS)

def save_flashcards_to_file(flashcards):
    """Handles saving flashcards to a text file via a UI selection process."""
    
    # Define UI states for navigation
    state = "select_file"  # Possible states: "select_mode", "new_file", "save_file", "done"
    selected_file = None
    file_path = None
    save_mode = None  # "a" for append, "w" for overwrite

    # Retrieve existing .txt files
    txt_files = [f for f in os.listdir() if f.endswith(".txt")]
    options = txt_files + ["Create New File"] if txt_files else ["Create New File"]

    def get_new_file_name(prompt):
        """Prompts user for a new filename using an input box."""
        input_box = pygame.Rect(WIDTH // 4, HEIGHT // 2, WIDTH // 2, 100)
        user_text = ""
        active = True

        while active:
            events = pygame.event.get()
            for event in events:
                check_quit_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        active = False  # Submit input
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]  # Remove last character
                    else:
                        user_text += event.unicode  # Add new character

            screen.fill(WHITE)
            prompt_surface = FONT.render(prompt, True, BLACK)
            screen.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT // 2 - 50))

            pygame.draw.rect(screen, BLACK, input_box, 2)  # Draw input box

            # Wrap user input text within box width constraints
            wrapped_lines = wrap_text(user_text, FONT, input_box.width - 10)
            for i, line in enumerate(wrapped_lines):
                screen.blit(FONT.render(line, True, BLACK), (input_box.x + 5, input_box.y + 5 + i * FONT.get_height()))

            pygame.display.flip()
            clock.tick(FPS)

        return user_text

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            check_quit_event(event)
        screen.fill(WHITE)

        # Display header text
        screen.blit(BIG_FONT.render("Save Flashcards as Text File", True, BLACK), (WIDTH // 2 - 200, 50))

        if state == "select_file":
            """STATE: Select a file to save flashcards or create a new one."""
            screen.blit(FONT.render("Select a file to save your flashcards:", True, BLACK), (WIDTH // 2 - 200, 110))

            button_width, button_height, margin, start_y = 400, 50, 20, 150
            file_buttons = [create_button(option, (WIDTH - button_width) // 2, start_y + i * (button_height + margin), button_width, button_height) for i, option in enumerate(options)]
            draw_button_list(file_buttons)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in file_buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            state = "new_file" if button["text"] == "Create New File" else "select_mode"
                            selected_file = button["text"]

        elif state == "select_mode":
            """STATE: Choose between Append or Overwrite for an existing file."""
            screen.blit(FONT.render(f"Selected File: {selected_file}", True, BLACK), (WIDTH // 2 - 200, 110))
            screen.blit(FONT.render("Choose mode:", True, BLACK), (WIDTH // 2 - 100, 150))

            left_rect, right_rect = create_button_pair(220, width=150, height=50, spacing=100)
            append_button = {"rect": left_rect, "text": "Append", "color": GRAY}
            overwrite_button = {"rect": right_rect, "text": "Overwrite", "color": GRAY}
            draw_button_list([append_button, overwrite_button])

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if left_rect.collidepoint(mouse_pos):
                        save_mode, file_path, state = "a", selected_file, "save_file"
                    elif right_rect.collidepoint(mouse_pos):
                        save_mode, file_path, state = "w", selected_file, "save_file"

        elif state == "new_file":
            """STATE: Prompt user for new filename."""
            file_name = get_new_file_name("Enter new file name (without extension):").strip() or "flashcards"
            file_path = f"{file_name}.txt" if not file_name.endswith(".txt") else file_name
            save_mode, state = "w", "save_file"

        elif state == "save_file":
            """STATE: Save flashcards to file."""
            try:
                with open(file_path, save_mode, encoding="utf-8") as f:
                    for card in flashcards:
                        f.write(f"Front: {card.front}\nBack:  {card.back}\n\n")
                show_feedback("Flashcards saved successfully!", duration=1500, color=GREEN)
            except Exception as e:
                show_feedback(f"Error: {e}", duration=2000, color=RED)
            state = "done"

        pygame.display.flip()
        clock.tick(FPS)

        if state == "done":
            running = False  # Exit loop once completed

def save_flashcards_mode(flashcards):
    """Provides options to display or save flashcards."""
    active = True
    while active:
        screen.fill(WHITE)
        title = BIG_FONT.render("Save Flashcards", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Create buttons for display and file save options
        button_display = pygame.Rect(WIDTH // 2 - 150, 150, 300, 50)
        button_file = pygame.Rect(WIDTH // 2 - 150, 250, 300, 50)
        draw_button("Display for Copy/Paste", button_display, GRAY)
        draw_button("Save to File", button_file, GRAY)
        pygame.display.flip()

        # Handle user interaction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if button_display.collidepoint(pos):
                    display_flashcards_text(flashcards)  # Show flashcards in text format
                    active = False  
                elif button_file.collidepoint(pos):
                    save_flashcards_to_file(flashcards)  # Save flashcards to a file
                    active = False   
        clock.tick(FPS)


def main_menu():
    """Main menu interface for flashcard application."""
    flashcards = []
    feedback_message = ""
    feedback_timer = 0

    while True:
        screen.fill(WHITE)
        
        # Display app title
        title_surface = BIG_FONT.render("Flashcard App", True, BLACK)
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 30))
        title_surface = BIG_FONT.render("(Press Return When Entering Text or Numbers)", True, BLACK)
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 75))

        # Display feedback message if one exists
        if feedback_message:
            feedback_timer -= 1
            if feedback_timer <= 0:
                feedback_message = ""
            else:
                feedback_text = FONT.render(feedback_message, True, RED)
                screen.blit(feedback_text, (WIDTH//2 - feedback_text.get_width()//2, 80))

        # Create menu buttons
        button_list = [
            create_button("Enter/Delete Flashcards", 50, 150, 300, 50),
            create_button("Shuffle Flashcards", 450, 150, 300, 50),
            create_button("Reverse Flashcards", 50, 250, 300, 50),
            create_button("Track Progress", 450, 250, 300, 50),
            create_button("Test Yourself", 50, 350, 300, 50),
            create_button("Save Flashcards", 450, 350, 300, 50),
            create_button("Exit", 250, 450, 300, 50)
        ]
        draw_button_list(button_list)
        pygame.display.flip()

        # Handle user interaction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for button in button_list:
                    if button["rect"].collidepoint(pos):
                        if button["text"] == "Enter/Delete Flashcards":
                            flashcards = handle_button_click(button["rect"], None, enter_flashcards)
                        elif button["text"] == "Shuffle Flashcards":
                            flashcards = handle_button_click(button["rect"], flashcards, animate_shuffle)
                        elif button["text"] == "Reverse Flashcards":
                            flashcards = handle_button_click(button["rect"], flashcards, animate_reverse)
                        elif button["text"] == "Track Progress":
                            handle_button_click(button["rect"], flashcards, track_progress_mode)
                        elif button["text"] == "Test Yourself":
                            handle_button_click(button["rect"], flashcards, test_yourself_mode)
                        elif button["text"] == "Save Flashcards":
                            handle_button_click(button["rect"], flashcards, save_flashcards_mode)
                        elif button["text"] == "Exit":
                            pygame.quit()
                            sys.exit()
                        break
        clock.tick(FPS)

# Start the application
main_menu()