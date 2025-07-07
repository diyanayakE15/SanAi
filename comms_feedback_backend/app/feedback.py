def generate_feedback(metrics: dict):
    fb = []
    if metrics.get("clarity", 0) < 60:
        fb.append("Work on clarity: try slower pacing.")
    if len(metrics.get("grammar_errors", [])) > 2:
        fb.append("Check grammar: several minor errors.")
    if metrics.get("sentiment", {}).get("label") == "NEGATIVE":
        fb.append("Tone seems negative; consider expressing more positivity.")
    return fb

