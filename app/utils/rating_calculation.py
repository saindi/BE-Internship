
def get_rating(results) -> float:
    sum_correct = sum(result.count_correct_answers for result in results)
    count_questions = sum(result.count_questions for result in results)

    return sum_correct / count_questions
