def test_home_page_opens(client):
    response = client.get("/")

    assert response.status_code == 200


def test_about_page_opens(client):
    response = client.get("/about")

    assert response.status_code == 200
