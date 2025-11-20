import streamlit as st
import time
import random

# --- CONFIGURATION ---
GRID_SIZE = 20
TILE_SIZE = "15px"
INITIAL_SPEED = 0.2  # Seconds to wait between moves (lower is faster)

# --- SESSION STATE INITIALIZATION ---

def initialize_game_state():
    """Sets up the initial state of the game in Streamlit's session state."""
    if 'snake' not in st.session_state:
        st.session_state.snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        st.session_state.direction = (0, 1)  # (dx, dy): Start moving right
        st.session_state.food = place_food()
        st.session_state.score = 0
        st.session_state.game_over = False
        st.session_state.is_playing = False
        st.session_state.speed = INITIAL_SPEED

def place_food():
    """Places the food in a random cell that is not currently occupied by the snake."""
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if (x, y) not in st.session_state.snake:
            return (x, y)

def handle_direction(new_direction):
    """Updates the snake's direction, preventing immediate reversal."""
    if st.session_state.game_over:
        return
    current_dx, current_dy = st.session_state.direction
    new_dx, new_dy = new_direction

    # Prevent turning 180 degrees instantly (e.g., Left while moving Right)
    if (new_dx, new_dy) != (-current_dx, -current_dy):
        st.session_state.direction = new_direction

def reset_game():
    """Resets all game variables and restarts the loop."""
    st.session_state.snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
    st.session_state.direction = (0, 1)
    st.session_state.food = place_food()
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.is_playing = True
    st.session_state.speed = INITIAL_SPEED
    # Force a rerun to start the game loop
    st.rerun()

# --- GAME LOGIC ---

def move_snake_logic():
    """Calculates the new head position and updates the snake body."""
    dx, dy = st.session_state.direction
    head_x, head_y = st.session_state.snake[0]
    new_head = (head_x + dx, head_y + dy)

    # 1. Check for collision (Wall or Self)
    if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or
        new_head[1] < 0 or new_head[1] >= GRID_SIZE or
        new_head in st.session_state.snake):
        st.session_state.game_over = True
        st.session_state.is_playing = False
        return

    # 2. Add new head
    st.session_state.snake.insert(0, new_head)

    # 3. Check for food
    if new_head == st.session_state.food:
        st.session_state.score += 1
        st.session_state.food = place_food()
        # Increase speed slightly every 5 points (optional speedup)
        if st.session_state.score % 5 == 0 and st.session_state.speed > 0.05:
            st.session_state.speed *= 0.95
    else:
        # 4. Remove tail (only if no food was eaten)
        st.session_state.snake.pop()

# --- RENDERING ---

def render_board(placeholder):
    """Generates the HTML/CSS grid representation and updates the placeholder."""

    # Define CSS styles for the board and elements
    styles = f"""
    <style>
        .snake-grid {{
            display: grid;
            grid-template-columns: repeat({GRID_SIZE}, {TILE_SIZE});
            grid-template-rows: repeat({GRID_SIZE}, {TILE_SIZE});
            border: 2px solid #333;
            background-color: #222; /* Darker background */
            margin: 20px auto; /* Center the board */
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }}
        .tile {{
            width: 100%;
            height: 100%;
        }}
        .snake-head {{
            background-color: #4CAF50; /* Green for head */
            border-radius: 4px;
            box-shadow: 0 0 5px #7CFC00;
        }}
        .snake-body {{
            background-color: #66BB6A; /* Lighter green for body */
            border-radius: 2px;
        }}
        .food {{
            background-color: #FF5722; /* Orange/Red for food */
            border-radius: 50%;
            animation: pulse 1s infinite alternate;
        }}
        @keyframes pulse {{
            from {{ transform: scale(0.8); opacity: 0.8; }}
            to {{ transform: scale(1.0); opacity: 1.0; }}
        }}
        .center-content {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
    </style>
    """

    # Generate the grid HTML
    grid_html = '<div class="snake-grid">'
    snake_head = st.session_state.snake[0]
    food_x, food_y = st.session_state.food

    # Iterate through the grid rows (x) and columns (y)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            tile_class = "tile"
            is_snake = (x, y) in st.session_state.snake
            is_head = (x, y) == snake_head
            is_food = (x, y) == (food_x, food_y)

            if is_head:
                tile_class += " snake-head"
            elif is_snake:
                tile_class += " snake-body"
            elif is_food:
                tile_class += " food"

            grid_html += f'<div class="{tile_class}"></div>'

    grid_html += '</div>'

    # Combine styles and HTML and render it in the placeholder
    placeholder.markdown(styles + '<div class="center-content">' + grid_html + '</div>', unsafe_allow_html=True)


# --- MAIN APPLICATION ---

def app():
    st.set_page_config(layout="wide", page_title="Streamlit Snake Game")

    # Initialize the state before anything else
    initialize_game_state()

    st.title("🐍 Streamlit Snake Game")

    # Status and Score Display
    col1, col2 = st.columns([1, 1])
    col1.metric("Score", st.session_state.score)
    
    status_text = "Ready to Play!"
    if st.session_state.game_over:
        status_text = "💥 GAME OVER! Score: " + str(st.session_state.score)
    elif st.session_state.is_playing:
        status_text = "🟢 Playing..."

    col2.markdown(f"**Status:** {status_text}")


    # Game Board Placeholder
    game_placeholder = st.empty()


    # Control Panel
    st.markdown("<h3 style='text-align: center;'>Controls</h3>", unsafe_allow_html=True)
    control_cols = st.columns([1, 1, 1])

    with control_cols[1]:
        if st.button("🔼 Up", use_container_width=True):
            handle_direction((-1, 0))

    center_cols = st.columns([1, 1, 1])
    with center_cols[0]:
        if st.button("◀️ Left", use_container_width=True):
            handle_direction((0, -1))
    with center_cols[2]:
        if st.button("▶️ Right", use_container_width=True):
            handle_direction((0, 1))

    bottom_cols = st.columns([1, 1, 1])
    with bottom_cols[1]:
        if st.button("🔽 Down", use_container_width=True):
            handle_direction((1, 0))

    # Start/Reset Button
    if st.session_state.is_playing:
        if st.button("⏸️ Pause Game", use_container_width=True, type="secondary"):
            st.session_state.is_playing = False
            st.rerun() # Stop the loop
    elif st.session_state.game_over or not st.session_state.is_playing:
        button_text = "Start Game" if not st.session_state.game_over else "Play Again"
        if st.button(button_text, use_container_width=True, type="primary"):
            reset_game()


    # --- The Streamlit Game Loop Simulation ---
    # This block executes every time the script reruns (which is constantly when is_playing is True)
    if st.session_state.is_playing and not st.session_state.game_over:
        # 1. Move the snake
        move_snake_logic()
        
        # 2. Redraw the board
        render_board(game_placeholder)
        
        # 3. Wait for the game speed duration
        time.sleep(st.session_state.speed)
        
        # 4. Rerun the script immediately for the next frame
        st.rerun()
    
    # Render the final board state if the game is over or paused
    if st.session_state.game_over or not st.session_state.is_playing:
        render_board(game_placeholder)


if __name__ == '__main__':
    app()