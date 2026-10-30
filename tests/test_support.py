def test_eric_cartman_causes_handled_error(client):
    response = client.post(
        "/support",
        data={
            "name": "Эрик Картман",
            "email": "test@example.com",
            "message": "Проверка ошибки",
        },
    )

    page_text = response.get_data(as_text=True)

    assert response.status_code == 500

    assert (
        "Не удалось обработать ваш вопрос. "
        "Попробуйте отправить его позже."
        in page_text
    )
