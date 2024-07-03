from utils.rating_calculation import calculate_average_score


def avarage_quiz_score_by_time(data):
    data_by_date = {}
    for item in data:
        created_at_date = item['created_at'].date()
        if created_at_date not in data_by_date:
            data_by_date[created_at_date] = []
        data_by_date[created_at_date].append(item)

    result, history = [], []
    for date, data_list in data_by_date.items():
        history.extend(data_list)
        result.append({'date': date, 'rating': calculate_average_score(history)})

    return result


def user_last_pass_quizzes(data, quizzes_data):
    last_pass_dates = {}

    for item in data:
        id_quiz = item['id_quiz']
        created_at_date = item['created_at']

        if id_quiz in last_pass_dates:
            if created_at_date > last_pass_dates[id_quiz]["created_at"]:
                last_pass_dates[id_quiz] = item
        else:
            last_pass_dates[id_quiz] = item

    result = []
    for id_quiz, data in last_pass_dates.items():
         result.append({**data, "quiz_name": quizzes_data[id_quiz].name})

    return result


def company_users_last_pass_quizzes(data, users_data, quizzes_data):
    data_by_user = {}
    for item in data:
        user = item['id_user']
        if user not in data_by_user:
            data_by_user[user] = []
        data_by_user[user].append(item)

    user = []
    for user_id, results in data_by_user.items():
        time_last_pass = results[0]['created_at']
        for result in results:
            if result['created_at'] > time_last_pass:
                time_last_pass = result['created_at']

        result = {'id_user': user_id, 'date_last_pass': time_last_pass}

        user_data = users_data.get(user_id)
        if user_data:
            result.update({"email": user_data.email, "username": user_data.username})

        quiz_data = quizzes_data.get(user_id)
        if user_data:
            result.update({"quiz_name": quiz_data.name})

        user.append(result)

    return user
