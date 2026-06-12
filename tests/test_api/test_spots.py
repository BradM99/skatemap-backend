from uuid import uuid4
from http import HTTPStatus

from config import settings


class TestSpotEndpoints:
    """Test class for /spots API endpoints."""

    def test_create_spot(self, client):
        """Tests creating a spot returns the correct data."""
        spot_data = {
            "name": "Test Spot",
            "description": "This is a test spot",
            "latitude": 51.5074,
            "longitude": -0.1278
        }

        response = client.post("/spots/", json=spot_data)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data["name"] == spot_data["name"]
        assert data["description"] == spot_data["description"]
        assert data["latitude"] == spot_data["latitude"]
        assert data["longitude"] == spot_data["longitude"]
        assert "id" in data

    def test_get_all_spots(self, client):
        """Tests that a created spot appears in the list of all spots."""
        spot_data = {
            "name": "Test Spot",
            "description": "This is a test spot",
            "latitude": 51.5074,
            "longitude": -0.1278
        }

        response = client.post("/spots/", json=spot_data)
        assert response.status_code == HTTPStatus.CREATED
        created_id = response.json()["id"]

        response = client.get("/spots/")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        spot_ids = [s["id"] for s in data]
        assert created_id in spot_ids

    def test_get_spot_not_found(self, client):
        """Tests that a non-existent spot returns 404."""
        response = client.get(f"/spots/{uuid4()}")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_spot(self, client):
        """Tests that a spot can be updated."""
        spot_data = {
            "name": "Test Spot",
            "description": "This is a test spot",
            "latitude": 51.5074,
            "longitude": -0.1278
        }

        response = client.post("/spots/", json=spot_data)
        assert response.status_code == HTTPStatus.CREATED
        created_id = response.json()["id"]

        update_data = {"name": "New Name"}
        response = client.put(f"/spots/{created_id}", json=update_data)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["name"] == update_data["name"]

    def test_delete_spot(self, client, spot):
        """Tests that a spot can be deleted."""
        response = client.delete(f"/spots/{spot.id}")
        assert response.status_code == HTTPStatus.OK

    def test_delete_spot_doesnt_exist(self, client):
        """Tests that a non-existent spot returns 404."""
        response = client.delete(f"/spots/{uuid4()}")
        assert response.status_code == HTTPStatus.NOT_FOUND

class TestSpotImages:
    """Test class for /spots/{id}/images API endpoints."""

    test_image_dir = settings.BASE_DIR / "tests" / "test_images"

    def test_add_image(self, client, spot):
        """Tests uploading an image to a spot."""
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            response = client.post(f"/spots/{spot.id}/images", files={"file": f})
        assert response.status_code == HTTPStatus.CREATED
        assert "id" in response.json()

    def test_add_image_no_spot(self, client):
        """Tests that uploading to a non-existent spot returns 404."""
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            response = client.post(f"/spots/{uuid4()}/images", files={"file": f})
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_image(self, client, spot, temp_upload_dir):
        """Tests deleting an image removes the DB record and file from disk."""
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            post_response = client.post(f"/spots/{spot.id}/images", files={"file": f})
        assert post_response.status_code == HTTPStatus.CREATED

        image_id = post_response.json()["id"]
        file_path = temp_upload_dir / str(spot.id) / "test_spot.png"
        assert file_path.exists()

        delete_response = client.delete(f"/spots/{spot.id}/images/{image_id}")
        assert delete_response.status_code == HTTPStatus.OK
        assert not file_path.exists()

    def test_list_images(self, client, spot):
        """Tests that uploaded images are returned when listing a spot's images."""
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            response = client.post(f"/spots/{spot.id}/images", files={"file": f})
        assert response.status_code == HTTPStatus.CREATED

        with open(self.test_image_dir / "test_spot2.png", "rb") as f:
            response = client.post(f"/spots/{spot.id}/images", files={"file": f})
        assert response.status_code == HTTPStatus.CREATED

        response = client.get(f"/spots/{spot.id}/images")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 2
        filenames = {img["file_path"].replace("\\", "/").split("/")[-1] for img in data}
        assert "test_spot.png" in filenames
        assert "test_spot2.png" in filenames
