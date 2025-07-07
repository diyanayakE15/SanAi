import language_tool_python
from transformers import pipeline
from textstat import flesch_reading_ease

tool = language_tool_python.LanguageTool('en-US')
sentiment = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

def analyze_text(text: str):
    # Grammar
    matches = tool.check(text)
    grammar_errors = [m.ruleId for m in matches]

    # Clarity
    clarity = flesch_reading_ease(text)

    # Sentiment
    sent = sentiment(text)[0]  # dict with label + score

    return {
        "grammar_errors": grammar_errors,
        "clarity": clarity,
        "sentiment": sent
    }

