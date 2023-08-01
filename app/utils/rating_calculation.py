
def get_rating(results) -> float:
    sum_correct = sum(result.count_correct_answers for result in results)
    count_questions = sum(result.count_questions for result in results)

    return sum_correct / count_questions


def calculate_average_score(data_list):
    total_correct_answers = sum(item['count_correct_answers'] for item in data_list)
    total_questions = sum(item['count_questions'] for item in data_list)

    return total_correct_answers / total_questions
