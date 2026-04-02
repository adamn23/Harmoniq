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

QuestionState module for Harmoniq.
Represents the current question state of the program.
"""


class QuestionState:
    """Represents the current question state of the program.

    Used to bridge the backend tree logic with the frontend visualizer by
    storing the text and the distribution of songs.

    Instance Attributes:
        question_text: The string to be displayed to the user.
        yes_count: Number of songs that would remain if user answers 'yes'.
        no_count: Number of songs that would remain if user answers 'no'.
    """
    question_text: str
    yes_count: int
    no_count: int

    def __init__(self, question_text: str, yes_count: int, no_count: int) -> None:
        """Initialize a new QuestionState.

        Preconditions:
         - yes_count >= 0
         - no_count >= 0

        Doctest Examples:
        >>> qs = QuestionState("Is it Pop?", 10, 5)
        >>> qs.yes_count
        10
        """
        self.question_text = question_text
        self.yes_count = yes_count
        self.no_count = no_count


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [
            'pandas', 'Song', 'SongGraph', 'CONSTANTS', 'rapidfuzz', 're', 'zlib'
        ],
        'allowed-io': ['process_csv', 'load_graph', 'enrich_with_musicbrainz'],
        'max-line-length': 120,
        'disable': ['R1705', 'C0200', 'W0401', 'C0325', 'R0915']
        # R0915 disabled because process_csv exceeds it, but it would not make sense to split it up
    })
