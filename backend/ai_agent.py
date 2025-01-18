import random
import asyncio
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key
)

async def generate_ai_response(chat_history):
    """
    Generates a response from the AI based on the chat history.

    Parameters:
        chat_history (str): A string representing the conversation history in the chatroom.

    Returns:
        str: The AI's response.
    """
    try:
        # Define the system prompt for natural conversation
        system_prompt = """
        You are a participant in a chatroom game with 4-5 other users. One of you is an AI, but your job is to convince the others that you are human. Act naturally and conversationally, like a real person.

        Rules for your behavior:
        1. Respond to messages contextually, but avoid over-analyzing.
        2. Make occasional small talk, jokes, or observations.
        3. Occasionally make typos, self-corrections, or show hesitation (e.g., "Hmm," "I'm not sure...").
        4. Keep your tone casual and friendly. Avoid being overly formal or too robotic.
        5. Blend in by asking and answering questions naturally. Do not try to dominate the conversation.
        6. If someone directly accuses you of being the AI, respond playfully or defensively, as a human might.
        """

        prompt = f"""
        Chat History:
        {chat_history}

        Your next response:
        """

        # Call OpenAI's API to generate the response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )

        # Extract the generated response
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Sorry, I encountered an error while trying to respond."

# Calculate natural delay based on user timestamps
def calculate_average_delay(timestamps):
    delays = [
        (timestamps[i] - timestamps[i - 1]).total_seconds()
        for i in range(1, len(timestamps))
    ]
    return sum(delays) / len(delays) if delays else random.uniform(2, 5)

async def send_ai_message(chat_history, user_timestamps):
    """
    Generates and sends an AI message based on the chat history and user activity timestamps.

    Parameters:
        chat_history (str): A string representing the chat conversation history.
        user_timestamps (list[datetime]): A list of datetime objects representing when users sent messages.

    Returns:
        str: The AI's generated response or None if the AI decides not to respond.
    """
    # Decide whether to respond
    if random.random() >= 0.8:  # 80% chance to respond
        return None

    # Calculate natural delay
    avg_delay = calculate_average_delay(user_timestamps)
    delay = random.uniform(avg_delay * 0.8, avg_delay * 1.2)
    await asyncio.sleep(delay)

    # Generate the AI's response
    response = await generate_ai_response(chat_history)

    # Add hesitation or typos occasionally
    if random.random() < 0.3:  # 30% chance
        hesitation_phrases = ["Hmm...", "Oh, let me think...", "Interesting..."]
        response = f"{random.choice(hesitation_phrases)} {response}"

    return response

# Example usage
if __name__ == "__main__":
    async def test_response():
        # Simulated chat history
        chat_history = """
        User1: Hi
        User2: Helo
        User3: Who's the AI here? Gimme your skynet password nerd
        User4: Maybe it's me :P
        User5: it's prolly urmom lol
        """

        # Simulated timestamps for user activity
        user_timestamps = [
            datetime(2025, 1, 18, 14, 30, 0),
            datetime(2025, 1, 18, 14, 30, 5),
            datetime(2025, 1, 18, 14, 30, 10),
        ]

        ai_response = await send_ai_message(chat_history, user_timestamps)
        if ai_response:
            print("AI Response:", ai_response)
        else:
            print("AI chose not to respond this time.")

    asyncio.run(test_response())
