import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import json
import pandas as pd

# Set up the bingo goals
all_goals = [
    "Quit job dramatically", "Break up with partner",
    "Move abroad", "Failed business",
    "Back to school", "Existential crisis",
    "Delete social media", "Go vegan",
    "Unaffordable pet", "Join cult (briefly)",
    "Try influencing", "Date parents hate",
    "Expensive hobby", "Find yourself phase",
    "Credit card debt", "Crazy roommates",
    "Astrology phase", "Rebel upbringing",
    "Impractical purchase", "Ghost everyone",
    "Impulsive decision", "Regret degree",
    "Fake LinkedIn", "Compare to peers",
    "Need therapy", "Regret tattoo",
    "Temporary minimalism", "Binge-watch",
    "Food obsession", "Failed podcast"
]

def generate_card():
    selected = random.sample(all_goals, 25)
    card = []
    idx = 0
    for i in range(5):
        row = []
        for j in range(5):
            row.append(selected[idx])
            idx += 1
        card.append(row)
    return card

def draw_card(card, marked):
    img = Image.new('RGB', (800, 850), color='#f0f0f0')  # Light gray background
    draw = ImageDraw.Draw(img)

    # Draw title
    try:
        font = ImageFont.truetype("arialbd.ttf", 36)  # Bold Arial
    except:
        font = ImageFont.load_default()
    draw.text((200, 10), "Graduation Bingo", fill='black', font=font)

    # Grid properties
    cell_size = 140
    border_color = 'black'
    border_width = 3
    text_color = 'black'
    marked_color = '#90ee90'  # Light green
    center_color = '#fffacd'   # Light yellow
    font_size = 14

    for i in range(5):
        for j in range(5):
            x1, y1 = 50 + i * cell_size, 100 + j * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size

            # Fill marked squares
            if marked[i][j]:
                draw.rectangle([x1, y1, x2, y2], fill=marked_color)

            # Draw border
            draw.rectangle([x1, y1, x2, y2], outline=border_color, width=border_width)

            # Add text
            text = card[i][j]
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                st.error("Font file not found. Please ensure 'arial.ttf' is available.")
                font = ImageFont.load_default()

            # Center square formatting
            if i == 2 and j == 2:
                draw.rectangle([x1, y1, x2, y2], fill=center_color)
                font = ImageFont.truetype("arialbd.ttf", 16) if hasattr(ImageFont, 'truetype') else ImageFont.load_default()

            # Text wrapping
            lines = []
            words = text.split()
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if draw.textlength(test_line, font=font) <= cell_size - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            lines.append(' '.join(current_line))

            # Draw text lines
            y_offset = y1 + (cell_size / 2) - (len(lines) * font_size / 2)
            for line in lines:
                text_width = draw.textlength(line, font=font)
                draw.text((x1 + (cell_size / 2) - (text_width / 2), y_offset),
                          line, fill=text_color, font=font)
                y_offset += font_size + 2

    return img

def check_bingo(marked):
    # Check rows and columns
    for i in range(5):
        if all(marked[i][j] for j in range(5)) or all(marked[j][i] for j in range(5)):
            return True
    # Check diagonals
    if all(marked[i][i] for i in range(5)) or all(marked[i][4-i] for i in range(5)):
        return True
    return False

def save_to_excel(user_name, selected_goals):
    # Create a DataFrame with user data
    data = {"Name": [user_name], "Selected Goals": [", ".join(selected_goals)]}
    df = pd.DataFrame(data)

    # Save to an Excel file
    file_path = "user_activities.xlsx"
    try:
        # Append to the existing file if it exists
        existing_df = pd.read_excel(file_path)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(file_path, index=False)
    except FileNotFoundError:
        # Create a new file if it doesn't exist
        df.to_excel(file_path, index=False)

def main():
    st.set_page_config(layout="wide")
    st.title("🎓 Interactive Graduation Bingo")

    # Initialize session state
    if 'card' not in st.session_state:
        st.session_state.card = generate_card()
        st.session_state.marked = [[False]*5 for _ in range(5)]
        st.session_state.bingo = False
        st.session_state.selected_goals = set()

    # User input for name
    st.sidebar.header("User Information")
    user_name = st.sidebar.text_input("Enter your name:", key="user_name")

    if user_name:
        st.sidebar.success(f"Welcome, {user_name}!")

    # Create columns
    col1, col2 = st.columns([2, 1])

    with col1:
            st.subheader("Your Bingo Card")
            for i in range(5):
                cols = st.columns(5)
                for j in range(5):
                    is_marked = st.session_state.marked[i][j]
                    if is_marked:
                        button_color = "lightgreen"
                    elif i == 2 and j == 2:  # Center square
                        button_color = "lightyellow"
                    else:
                        button_color = "white"

                    button_label = st.session_state.card[i][j]
                    button_key = f"button_{i}_{j}"

                    # Create a unique key that includes the marked state
                    styled_button_key = f"{button_key}_{is_marked}"

                    if cols[j].button(
                        button_label,
                        key=styled_button_key,
                        help="Click to mark/unmark",
                    ):
                        st.session_state.marked[i][j] = not is_marked
                        st.session_state.bingo = check_bingo(st.session_state.marked)
                        # No st.rerun() here for this attempt

                    # Apply custom CSS based on the current marked state
                    cols[j].markdown(
                        f"""
                        <style>
                        div[data-testid="stButton"] > button[title="{button_label}"] {{
                            background-color: {button_color};
                            color: black;
                            font-weight: bold;
                            border: 1px solid black;
                            padding: 5px;
                            border-radius: 5px;
                            width: 100%;
                            height: 100%;
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )

            if st.session_state.bingo:
                st.balloons()
                st.success("🎉 BINGO! You won! 🎉")

    with col2:
        st.header("How to Play")
        st.markdown("""
        - **Click any square** on the Bingo card to mark/unmark it.
        - Complete a **row, column, or diagonal** to get Bingo!
        - The center square is marked in yellow.
        - Get 5 in a row to win!
        """)

        if st.button("Generate New Card"):
            st.session_state.card = generate_card()
            st.session_state.marked = [[False]*5 for _ in range(5)]
            st.session_state.bingo = False
            st.session_state.selected_goals.clear()

if __name__ == "__main__":
    main()
