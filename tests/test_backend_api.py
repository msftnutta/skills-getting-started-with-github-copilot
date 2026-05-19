def test_root_redirects_to_static_page(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload

    chess = payload["Chess Club"]
    assert {"description", "schedule", "max_participants", "participants"}.issubset(chess.keys())
    assert isinstance(chess["participants"], list)


def test_signup_success_adds_participant(client):
    activity_name = "Basketball"
    email = "new-student@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    activity_name = "Basketball"
    existing_email = "james@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_success_removes_participant(client):
    activity_name = "Tennis"
    email = "liam@mergington.edu"

    delete_response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete(
        "/activities/Unknown Club/participants", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Basketball/participants", params={"email": "not-registered@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_activities_reflect_changes_immediately_after_signup_and_unregister(client):
    activity_name = "Art Club"
    email = "refresh-check@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200

    after_signup = client.get("/activities")
    assert email in after_signup.json()[activity_name]["participants"]

    unregister_response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )
    assert unregister_response.status_code == 200

    after_unregister = client.get("/activities")
    assert email not in after_unregister.json()[activity_name]["participants"]