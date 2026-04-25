from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities as activities_data

client = TestClient(app)
original_activities = deepcopy(activities_data)


def setup_function():
    activities_data.clear()
    activities_data.update(deepcopy(original_activities))


def test_root_redirects_to_static_index():
    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Basketball" in response.json()


def test_signup_for_activity_success():
    # Arrange
    activity = "Tennis Club"
    email = "test_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities_data[activity]["participants"]


def test_signup_for_activity_activity_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_already_signed_up():
    # Arrange
    activity = "Basketball"
    email = "james@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success():
    # Arrange
    activity = "Art Club"
    email = "lucas@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities_data[activity]["participants"]


def test_remove_participant_not_found():
    # Arrange
    activity = "Drama Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_activity_not_found():
    # Arrange
    activity = "NoClub"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
