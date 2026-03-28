# Priority order for genre selection: more specific/niche genres beat generic ones.
# A song tagged "pop, rap, hip hop" will resolve to "hip hop" since it ranks highest.
# Pop is last because it is commonly added as a secondary tag to almost everything.
GENRE_PRIORITY = [
    'hip hop', 'rap', 'r&b', 'soul', 'jazz', 'blues', 'reggae', 'latin',
    'metal', 'rock', 'punk', 'indie', 'folk', 'country', 'classical',
    'electronic', 'dance', 'house', 'techno', 'edm', 'k-pop', 'pop'
]

IDEA_MAP = {
        'romance': r'\b(love|heart|baby|romance|kiss|forever|darling|mine)\b',
        'heartbreak': r'\b(cry|sad|broken|tears|lonely|pain|goodbye|hurt|leave)\b',
        'hustle': r'\b(money|rich|gold|success|win|grind|hustle|cash|bills|boss)\b',
        'partying': r'\b(club|party|dance|drink|tonight|bottles|dj|alcohol|shots)\b',
        'violence': r'\b(gun|kill|fight|blood|war|shot|death|dead|weapon)\b'
    }

# Similar concept to IDEA_MAP but with no heirarcy and higher song coverage
TOPIC_KEYWORDS = {
    "heartbreak": r"(?<!\w)("
                  r"heartbreak|heartbroken|brokenhearted|"
                  r"broken\s+heart(?:s)?|"
                  r"good(?:\s*-\s*|\s+)?bye|"
                  r"alone|lonely|"
                  r"tear|tears|"
                  r"cry|cries|crying|"
                  r"hurt|hurting|"
                  r"pain|painful|"
                  r"miss|missing|"
                  r"regret|regrets|"
                  r"sorry"
                  r")(?!\w)",

    "love": r"(?<!\w)("
            r"love|loved|loving|lover(?:s)?|"
            r"romance|romantic|"
            r"kiss|kissing|"
            r"crush|"
            r"date|dating|"
            r"girlfriend|boyfriend|"
            r"together|"
            r"forever|"
            r"honey|darling|baby|"
            r"valentine|"
            r"wedding|marry|married"
            r")(?!\w)",



    "wealth": r"(?<!\w)("
              r"money|cash|rich|wealth|"
              r"million|billion|"
              r"dollar|dollars|"
              r"gold|diamond|diamonds|"
              r"chain|chains|"
              r"gucci|rolex|bentley|ferrari|"
              r"flex|flexing|"
              r"drip|"
              r"ice|iced\s+out|"
              r"ballin|balling|"
              r"stack|stacks|"
              r"bankroll|"
              r"paid"
              r")(?!\w)",

    "intimacy": r"(?<!\w)("
                r"sex|sexy|"
                r"bed|bedroom|"
                r"touch|touching|"
                r"body|"
                r"naked|"
                r"desire|"
                r"lust|"
                r"hook(?:\s*-\s*|\s+)?up|"
                r"turn(?:\s*-\s*|\s+)?on|"
                r"make\s+out|"
                r"kiss(?:es|ing)?"
                r")(?!\w)",

    "religion": r"(?<!\w)("
                r"god|jesus|lord|allah|"
                r"church|mosque|temple|synagogue|"
                r"bible|quran|koran|torah|"
                r"pray|prayer|praying|amen|"
                r"faith|spirit|spiritual|"
                r"hallelujah|"
                r"heaven|hell|"
                r"sin|sinner|"
                r"angel|angels|devil"
                r")(?!\w)",


    "family": r"(?<!\w)("
              r"family|"
              r"mom|mother|mama|"
              r"dad|father|papa|"
              r"son|daughter|"
              r"home|hometown|"
              r"memories|memory|"
              r"childhood|"
              r"growing\s+up|"
              r"miss\s+home"
              r")(?!\w)",

    "hustle": r"(?<!\w)("
              r"hustle|hustling|"
              r"grind|grinding|"
              r"work|working|"
              r"ambition|"
              r"dream|dreams|"
              r"goal|goals|"
              r"success|"
              r"win|winning|"
              r"rise|rising|"
              r"made\s+it|"
              r"on\s+my\s+way"
              r")(?!\w)",


    "struggle": r"(?<!\w)("
                r"struggle|struggling|"
                r"hard\s+times|"
                r"broke|"
                r"hungry|"
                r"survive|survival|"
                r"pain|"
                r"suffer|suffering|"
                r"lonely|"
                r"tears|"
                r"stress|"
                r"wounds?"
                r")(?!\w)",


    "confidence": r"(?<!\w)("
                  r"confident|confidence|"
                  r"strong|stronger|"
                  r"power|powerful|"
                  r"boss|"
                  r"queen|king|"
                  r"i\s*'?m\s+the\s+best|"
                  r"unstoppable|"
                  r"independent|"
                  r"self\s*-\s*love|self\s+love|"
                  r"shine|"
                  r"on\s+top"
                  r")(?!\w)",


    "mental_health": r"(?<!\w)("
                     r"anxiety|"
                     r"depression|depressed|"
                     r"therapy|"
                     r"trauma|"
                     r"healing|heal|"
                     r"panic|"
                     r"insomnia|"
                     r"stress|"
                     r"lonely|"
                     r"empty|"
                     r"numb|"
                     r"overthinking"
                     r")(?!\w)",

    "violence": r"(?<!\w)("
                r"gun|guns|"
                r"shoot|shooting|"
                r"kill|killing|"
                r"blood|"
                r"murder|"
                r"fight|fighting|"
                r"crime|"
                r"jail|prison|"
                r"gang|"
                r"rob|robbery|"
                r"violence"
                r")(?!\w)",


    "politics": r"(?<!\w)("
                r"politics|political|"
                r"president|"
                r"government|"
                r"protest|protesting|"
                r"revolution|"
                r"freedom|"
                r"rights?|"
                r"justice|"
                r"racism|"
                r"war|"
                r"police|"
                r"equality|"
                r"oppression"
                r")(?!\w)",


    "good_vibes": r"(?<!\w)("
                  r"good\s+vibes|"
                  r"feel\s+good|"
                  r"happy|happiness|"
                  r"smile|smiling|"
                  r"celebrate|celebration|"
                  r"sunshine|"
                  r"summer|"
                  r"beautiful|"
                  r"good\s+time|good\s+times|"
                  r"alright|"
                  r"we\s+made\s+it"
                  r")(?!\w)",

    "party": r"(?<!\w)("
             r"party|partying|"
             r"club|nightclub|"
             r"dance|dancing|"
             r"turn(?:\s*-\s*|\s+)?up|"
             r"lit|"
             r"drink|drinks|drinking|"
             r"vodka|whiskey|tequila|champagne|"
             r"shots?|"
             r"tonight|"
             r"weekend"
             r")(?!\w)",
}
