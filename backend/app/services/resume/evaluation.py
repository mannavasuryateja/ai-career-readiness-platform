def compute_metrics(predicted, ground_truth):

    predicted_set = set(predicted)
    truth_set = set(ground_truth)

    tp = len(predicted_set & truth_set)
    fp = len(predicted_set - truth_set)
    fn = len(truth_set - predicted_set)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }
