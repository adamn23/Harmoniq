
class QuestionState:
    """
    Represents the current question and dialogue state of the program
    """
    dialogue_text: str
    question_text: str
    yes_count: int
    no_count: int

    def __init__(self, dialogue_text: str, question_text: str,
                 yes_count: int, no_count: int) -> None:
        self.dialogue_text = dialogue_text
        self.question_text = question_text
        self.yes_count = yes_count
        self.no_count = no_count
