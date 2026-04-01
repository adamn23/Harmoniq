
class QuestionState:
    """
    Represents the current question state of the program
    """
    question_text: str
    yes_count: int
    no_count: int

    def __init__(self, question_text: str,
                 yes_count: int, no_count: int) -> None:
        self.question_text = question_text
        self.yes_count = yes_count
        self.no_count = no_count
