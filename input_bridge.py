"""
This file uses Python's built-in Queue ADT to facilitate communication between pygame,
the console, and the backend of the program.
This allows us to run the game using pygame and console as inputs simultaneously!
"""
from queue import Queue
import threading

answer_queue: Queue[tuple[str, str]] = Queue()  # (Answer, Source (pygame or console))
prompt_ready = threading.Event()


def wait_and_handle_console_input() -> None:
    """
    Waits for user input from the console and enqueues it
    """
    while True:
        # waits for the game backend in main.py to indicate that the current question has been prepared
        prompt_ready.wait()
        while True:
            answer = input().strip().lower()
            if answer in {"yes", "no", "idk", "i don't know", "i dont know"}:
                answer_queue.put((answer, 'console'))
                prompt_ready.clear()
                break
            else:
                print("Please answer with Yes, No, or I don't know.")


def start_console_input_thread() -> None:
    """
    Begins a console input thread (via wait_and_handle_console_input()) that runs in the background
    so that answers fed into the console can be processed without blocking pygame.
    Allows the console and pygame to run and recieve input simultaneously without conflict.
    """
    thread = threading.Thread(target=wait_and_handle_console_input, daemon=True)
    thread.start()







