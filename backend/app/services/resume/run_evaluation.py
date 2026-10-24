import json
from app.services.resume.evaluation import compute_metrics
from app.services.resume.weighted_scoring import calculate_weighted_skill_score
from app.services.resume.parser import normalize_with_onet




def run_evaluation(dataset_path="evaluation_dataset.json"):

    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    evaluation_pairs = dataset["evaluation_pairs"]

    TP = FP = TN = FN = 0
    total_precision = total_recall = total_f1 = 0
    valid_pairs = 0

    for pair in evaluation_pairs:

        resume = pair["resume_skills"]
        jd = pair["jd_skills"]

        # Normalize inputs
        normalized_resume = normalize_with_onet(resume)
        normalized_jd = normalize_with_onet(jd)

        predicted = list(set(normalized_resume) & set(normalized_jd))

        # Normalize ground truth
        ground_truth_raw = pair["true_matched_skills"]
        ground_truth = normalize_with_onet(ground_truth_raw)

        # ---- Skill-level metrics ----
        if len(ground_truth) > 0:
            metrics = compute_metrics(predicted, ground_truth)
            total_precision += metrics["precision"]
            total_recall += metrics["recall"]
            total_f1 += metrics["f1_score"]
            valid_pairs += 1

        # ---- Binary Match Classification ----
        true_label = 1 if len(ground_truth) > 0 else 0
        predicted_label = 1 if len(predicted) > 0 else 0

        if true_label == 1 and predicted_label == 1:
            TP += 1
        elif true_label == 0 and predicted_label == 1:
            FP += 1
        elif true_label == 0 and predicted_label == 0:
            TN += 1
        elif true_label == 1 and predicted_label == 0:
            FN += 1

    avg_precision = total_precision / valid_pairs
    avg_recall = total_recall / valid_pairs
    avg_f1 = total_f1 / valid_pairs

    accuracy = (TP + TN) / len(evaluation_pairs)

    print("\n==== Skill Matching Metrics ====")
    print(f"Average Precision: {round(avg_precision, 3)}")
    print(f"Average Recall: {round(avg_recall, 3)}")
    print(f"Average F1 Score: {round(avg_f1, 3)}")

    print("\n==== Confusion Matrix ====")
    print(f"TP: {TP}")
    print(f"FP: {FP}")
    print(f"TN: {TN}")
    print(f"FN: {FN}")
    print(f"Matching Accuracy: {round(accuracy, 3)}")


if __name__ == "__main__":
    run_evaluation()
