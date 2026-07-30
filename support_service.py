def process_support_question(user_name, email, message):
    user_name = user_name.strip()
    email = email.strip()
    message = message.strip()

    if not user_name or not email or not message:
        raise ValueError("Заполните все поля формы.")

    return {
        "user_name": user_name,
        "email": email,
        "message": message,
    }
