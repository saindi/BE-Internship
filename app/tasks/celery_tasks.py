from datetime import datetime, timezone

from celery import Celery
from celery.schedules import crontab

from company.models.models import CompanyModel, RoleModel
from config import global_settings
from db.database import get_sync_session
from quiz.models.models import ResultTestModel
from user.models.models import UserModel, NotificationModel

celery = Celery('tasks', broker=global_settings.redis_url, backend=global_settings.redis_url)

celery.conf.timezone = 'Europe/Kiev'


@celery.task()
def check_for_need_pass_quizzes_users():
    session = get_sync_session()

    users = session.query(UserModel).all()

    for user in users:
        user_companies = [session.query(CompanyModel).get(role.id_company) for role in
                          session.query(RoleModel).filter_by(id_user=user.id)]

        for company in user_companies:
            for quiz in company.quizzes:
                results = session.query(ResultTestModel).filter_by(
                    id_user=user.id,
                    id_quiz=quiz.id
                ).all()

                if results:
                    latest_result = max(results, key=lambda result: result.created_at)

                    now_datetime = datetime.now(timezone.utc)

                    if (now_datetime - latest_result.created_at).total_seconds() > quiz.count_day * 24 * 60 * 60:
                        session.add(
                            NotificationModel(
                                id_user=user.id,
                                text=f"It's been a long time since you've had a quiz {quiz.name} at {company.name}!"
                            )
                        )
                else:
                    session.add(
                        NotificationModel(
                            id_user=user.id,
                            text=f"You have not yet passed the test {quiz.name} in the company {company.name}!"
                        )
                    )

                session.commit()

    session.close()


celery.conf.beat_schedule = {
    'check_last_pass_quiz': {
        'task': 'celery_tasks.tasks.check_for_need_pass_quizzes_users',
        'schedule': crontab(hour=0, minute=0),
    }
}
