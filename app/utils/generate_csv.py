import io
import pandas as pd


def get_csv(flattened_data):
    df = pd.DataFrame(flattened_data)

    output = io.StringIO()

    df.to_csv(output, index=False)

    output.seek(0)

    return io.BytesIO(output.getvalue().encode())


def generate_csv_data_as_result(data: dict):
    flattened_data = []
    for question in data["questions"]:
        row = {
            "id": data["id"],
            "id_user": data["id_user"],
            "id_company": data["id_company"],
            "id_quiz": data["id_quiz"],
            "created_at": data["created_at"],
            "question": question["question"],
            "answer_is_correct": question["answer_is_correct"],
            "user_answers": ", ".join(question["user_answers"])
        }
        flattened_data.append(row)

    return get_csv(flattened_data)


def generate_csv_data_as_results(data_list: list):
    flattened_data = []
    for data in data_list:
        for question in data["questions"]:
            row = {
                "id": data["id"],
                "id_user": data["id_user"],
                "id_company": data["id_company"],
                "id_quiz": data["id_quiz"],
                "created_at": data["created_at"],
                "question": question["question"],
                "answer_is_correct": question["answer_is_correct"],
                "user_answers": ", ".join(question["user_answers"])
            }
            flattened_data.append(row)

    return get_csv(flattened_data)
