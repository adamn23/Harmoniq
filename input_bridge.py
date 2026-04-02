"""
Harmoniq - Song Guessing Engine

Copyright (c) 2026 Adam Ahmed, Omer Sheaffer. All rights reserved.

This software and all associated documentation files (the "Software") are the property of the copyright holder.
No part of this Software may be reproduced, transmitted, distributed, modified, or otherwise used, in whole or in part,
in any form or by any means, whether electronic, mechanical, photocopying, recording, or otherwise, without the prior
express written permission of the copyright holder.

The unauthorized use, copying, or distribution of this Software is strictly prohibited and may result in civil and/or
criminal penalties under applicable law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE
LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM,
OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This file uses Python's built-in Queue ADT to facilitate communication between pygame,
the console, and the backend of the program.
This allows us to run the game using pygame and console as inputs simultaneously!
"""
from queue import Queue
import threading

ANSWER_QUEUE: Queue[tuple[str, str]] = Queue()  # (Answer, Source (pygame or console))
PROMPT_READY = threading.Event()


def wait_and_handle_console_input() -> None:
    """Wait for user input from the console and enqueue it for processing.

    Blocks until PROMPT_READY is set, then continuously prompts the user
    until a valid answer is provided. Enqueues the result with a 'console' tag.

    Preconditions:
        - PROMPT_READY event is initialized.
        - ANSWER_QUEUE is initialized.

    Doctest Examples:
    >>> # This function runs a blocking loop; usually tested via threading.
    >>> wait_and_handle_console_input() # doctest: +SKIP
    """
    while True:
        # waits for the game backend in main.py to indicate that the current question has been prepared
        PROMPT_READY.wait()
        while True:
            answer = input().strip().lower()
            if answer in {"yes", "no", "idk", "i don't know", "i dont know"}:
                ANSWER_QUEUE.put((answer, 'console'))
                PROMPT_READY.clear()
                break
            else:
                print("Please answer with Yes, No, or I don't know.")


def start_console_input_thread() -> None:
    """Begin a background thread to handle console inputs.

    Initializes a daemon thread to run wait_and_handle_console_input so that
    the console can receive answers without blocking the Pygame UI loop.

    Preconditions:
        - None

    Doctest Examples:
    >>> start_console_input_thread() # doctest: +SKIP
    """
    thread = threading.Thread(target=wait_and_handle_console_input, daemon=True)
    thread.start()


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [
            'queue', 'threading'
        ],
        'allowed-io': ['wait_and_handle_console_input'],
        'max-line-length': 120,
        'disable': ['R1705', 'C0200', 'W0401', 'C0325', 'R0915', 'E9992']
        # E9992 disabled because ANSWER_QUEUE and PROMPT_READY must be
        # module-level globals so they can be imported and shared across
        # game_visualization, main, and input_bridge simultaneously.
    })
