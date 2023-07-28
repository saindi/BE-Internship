
def get_rating(results) -> float:
    sum_correct, count_questions = 0, 0
    for result in results:
        sum_correct += result.count_correct_answers
        count_questions += result.count_questions

    return sum_correct / count_questions
