def compute_score(metrics: dict):
    weights = {
        "clarity": 0.2, "fluency": 0.2,
        "grammar": 0.2, "prosody": 0.2, "sentiment": 0.2}
    score = sum(metrics[k]*weights.get(k, 0) for k in metrics)
    return round(score, 2)

