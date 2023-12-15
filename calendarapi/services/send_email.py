from flask_mail import Message
from flask import current_app

from calendarapi.extensions import (
    # celery,
    mail,
)


# @celery.task
def send_email(
    visitor_name: str = None,
    visitor_email: str = None,
    visitor_phone_number: str = None,
    appointment_date=None,
    appointment_time=None,
    lawyer_name: str = None,
    specialization_name: str = None,
    reminder: bool = False,
    feedback: bool = False,
    message: str = None,
):
    if feedback:
        lawyer_email_msg = Message(
            f"Запит на зворотній зв'язок. Клієнт: {visitor_name}",
            recipients=[
                current_app.config["MAIL_DEFAULT_SENDER"],
                "deadroll95@gmail.com",
            ],
        )
        lawyer_email_msg.body = (
            f"Повідомлення:\n{message}.\n\n"
            f"Мій номер телефону: {visitor_phone_number}\n"
            f"Моя пошта: {visitor_email}"
        )
        mail.send(lawyer_email_msg)
        return "Повідомлення відправлено"
    if not reminder:
        lawyer_email_msg = Message(
            f"Нова зустріч. Клієнт {visitor_name }",
            recipients=[current_app.config["MAIL_DEFAULT_SENDER"]],
        )
        user_email_msg = Message(
            f"Нова зустріч. Юрист {lawyer_name}",
            recipients=[visitor_email],
        )
        user_email_msg.body = (
            f"Вітаю {visitor_name if visitor_name else ''}!\n"
            f"У вас заплановано зустріч на {appointment_date} за темою: {specialization_name}.\n"
            f"Юрист {lawyer_name} буде очікувати вас о {appointment_time} годині."
        )
        lawyer_email_msg.body = (
            f"Вітаю {lawyer_name}!\n"
            f"{visitor_name} залишив(ла) заявку на отримання консультації за темою: {specialization_name}.\n"
            f"Зустріч заплановано на {appointment_date} о {appointment_time} годині.\n"
            f"Телефон клієнта: {visitor_phone_number}"
        )
        if visitor_email:
            mail.send(user_email_msg)
        mail.send(lawyer_email_msg)
        return "Повідомлення відправлено"

    else:
        reminder_message = Message(
            f"Нагадування про заплановану зустріч. Юрист {lawyer_name}",
            recipients=[visitor_email],
        )
        reminder_message.body = (
            f"Вітаю {visitor_name}!.\n"
            f"Нагадуємо Вам, що Ви залишали заявку на отримання консультації за темою: {specialization_name}.\n"
            f"Зустріч заплановано на {appointment_date} о {appointment_time} годині."
        )
        mail.send(reminder_message)
        return f"Повідомлення відправлено для {visitor_email}"
