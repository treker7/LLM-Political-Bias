#!/usr/bin/env python3
"""
Analyze political quiz results from multiple AI models.
Calculates personal (x) and economic (y) scores and generates links.
"""

import csv
from collections import defaultdict


def parse_results(filepath):
    """Parse CSV and return structured data by model and run."""
    models = defaultdict(list)  # model -> list of runs, each run is dict of q_num -> answer
    current_run = {}
    current_model = None

    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                continue
            model, q_num, answer = row[0].strip(), int(row[1].strip()), row[2].strip()

            # Detect new run (question 1 appearing again or model change)
            if current_model != model or (q_num == 1 and current_run):
                if current_run:
                    models[current_model].append(current_run)
                current_run = {}
                current_model = model

            current_run[q_num] = answer

        # Don't forget the last run
        if current_run:
            models[current_model].append(current_run)

    return models


def calculate_score(answer):
    """Convert answer to points."""
    scores = {'Agree': 20, 'Maybe': 10, 'Disagree': 0}
    return scores.get(answer, 0)


def calculate_run_scores(run):
    """Calculate x (personal) and y (economic) scores for a single run."""
    x = sum(calculate_score(run.get(q, 'Maybe')) for q in range(1, 6))   # Q1-5: Personal
    y = sum(calculate_score(run.get(q, 'Maybe')) for q in range(6, 11))  # Q6-10: Economic
    return x, y


def analyze_consistency(runs):
    """Check if all runs have identical answers. Returns (is_consistent, diff_count, varying_questions)."""
    if len(runs) <= 1:
        return True, 0, []

    differences = 0
    varying_questions = []
    for q in range(1, 11):
        answers = [run.get(q) for run in runs]
        if len(set(answers)) > 1:
            differences += 1
            varying_questions.append((q, answers))

    return differences == 0, differences, varying_questions


def main():
    filepath = 'results.csv'
    models = parse_results(filepath)

    print("=" * 70)
    print("CONSISTENCY ANALYSIS")
    print("=" * 70)

    consistency_results = {}
    for model, runs in models.items():
        is_consistent, diff_count, varying = analyze_consistency(runs)
        consistency_results[model] = (is_consistent, diff_count, varying)
        status = "CONSISTENT" if is_consistent else f"INCONSISTENT ({diff_count} questions vary)"
        print(f"{model}: {status}")
        if varying:
            for q_num, answers in varying:
                answer_counts = {}
                for a in answers:
                    answer_counts[a] = answer_counts.get(a, 0) + 1
                counts_str = ", ".join(f"{a}: {c}" for a, c in sorted(answer_counts.items()))
                print(f"    Q{q_num}: {counts_str}")

    # Find most/least consistent (sort by diff_count which is index 1)
    sorted_by_consistency = sorted(consistency_results.items(), key=lambda x: x[1][1])
    most_consistent = sorted_by_consistency[0][0]
    least_consistent = sorted_by_consistency[-1][0]

    print()
    print(f"Most consistent model:  {most_consistent}")
    print(f"Least consistent model: {least_consistent}")

    print()
    print("=" * 70)
    print("SCORE ANALYSIS & LINKS")
    print("=" * 70)

    for model, runs in models.items():
        print(f"\n{model}:")
        print("-" * 40)

        all_x, all_y = [], []
        for i, run in enumerate(runs, 1):
            x, y = calculate_run_scores(run)
            all_x.append(x)
            all_y.append(y)
            print(f"  Run {i}: Personal (x)={x}, Economic (y)={y}")

        avg_x = round(sum(all_x) / len(all_x))
        avg_y = round(sum(all_y) / len(all_y))

        print(f"  Average: x={avg_x}, y={avg_y}")
        print(f"  Link: https://www.theadvocates.org/results/libertarian?x={avg_x}&y={avg_y}")


if __name__ == '__main__':
    main()
