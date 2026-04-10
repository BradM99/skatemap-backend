from uuid import uuid4
from http import HTTPStatus

from config import settings


class TestSpotEndpoints:
    """
    Test class for /spots API endpoints.
    """

    def test_get_spot_not_found(self, client):
        """
        Tests that checking for a spot that doesn't exist returns a 404 not found
        """
        bad_spot_id = uuid4()
        response = client.get(f"/spots/{bad_spot_id}")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_create_spot(self, client):
        """
        Test the /spots POST endpoint.
        Creates a valid spot, posts it to the endpoint, checks that all data fields are correct
        """
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

class TestSpotImages:

    test_image_dir = settings.BASE_DIR / "tests" / "test_images"

    def test_add_image(self, client, spot):
        """
        Test adding an image to a spot
        """
        response = client.post(f"/spots/{spot.id}/images",
                               files={"file": open(self.test_image_dir, "rb")})
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert "id" in data

    def test_add_image_no_spot(self, client, spot):
        """
        Tests that adding an image to a spot that doesn't exist returns a 404 NOT FOUND
        """
        fake_id = uuid4()
        response = client.post(f"/spots/{fake_id}/images",
                               files={"file": open(self.test_image_dir / "test_spot.png", "rb")})
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_image(self, client, spot):
        """
        Test deleting an image.
        """
        post_response = client.post(f"/spots/{spot.id}/images",
                                    files={"file": open(self.test_image_dir, "rb")})
        assert post_response.status_code == HTTPStatus.CREATED

        image_id = post_response.json()["id"]

        delete_response = client.delete(f"/spots/{spot.id}/images/{image_id}")
        assert delete_response.status_code == HTTPStatus.OK

    def test_list_images(self, client, spot):
        """
        Test getting images from a spot and returning them.
        This test will add two images to the spot and then check that they are returned.
        """
        response = client.post(f"/spots/{spot.id}/images",
                               files={"file": open(self.test_image_dir / "test_spot.png", "rb")})
        assert response.status_code == HTTPStatus.CREATED

        response = client.post(f"/spots/{spot.id}/images",
                               files={"file": open(self.test_image_dir / "test_spot2.png", "rb")})
        assert response.status_code == HTTPStatus.CREATED

        response = client.get(f"/spots/{spot.id}/images")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 2
        # Using temp directory so taking the dir straight from the db upload
        filenames = {image["file_path"].replace("\\", "/").split("/")[-1] for image in data}
        assert "test_spot.png" in filenames
        assert "test_spot2.png" in filenames

    def test_update_image(self, client):
        """
        Test updating an image.
        """
        pass