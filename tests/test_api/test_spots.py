from http import HTTPStatus
from uuid import uuid4

from config import settings, MAX_FILE_SIZE


class TestSpotEndpoints:
    """Test class for /spots API endpoints."""

    def test_create_spot(self, client, auth_headers):
        """Tests creating a spot returns the correct data."""
        spot_data = {
            "name": "Test Spot",
            "description": "This is a test spot",
            "latitude": 51.5074,
            "longitude": -0.1278
        }

        response = client.post("/spots/", json=spot_data, headers=auth_headers)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data["name"] == spot_data["name"]
        assert data["description"] == spot_data["description"]
        assert data["latitude"] == spot_data["latitude"]
        assert data["longitude"] == spot_data["longitude"]
        assert "id" in data

    def test_get_all_spots(self, client, spots):
        """Tests that created spots appear in the list of all spots."""
        response = client.get("/spots/", params={"offset": 0, "limit": 10})
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        spot_ids = [s["id"] for s in data]

        for spot in spots:
            assert spot["id"] in spot_ids

    def test_get_spot_not_found(self, client):
        """Tests that a non-existent spot returns 404."""
        response = client.get(f"/spots/{uuid4()}")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_spot(self, client, auth_headers):
        """Tests that a spot can be updated."""
        spot_data = {
            "name": "Test Spot",
            "description": "This is a test spot",
            "latitude": 51.5074,
            "longitude": -0.1278
        }

        response = client.post("/spots/", json=spot_data, headers=auth_headers)
        assert response.status_code == HTTPStatus.CREATED
        created_id = response.json()["id"]

        update_data = {"name": "New Name"}
        response = client.put(f"/spots/{created_id}", json=update_data, headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["name"] == update_data["name"]

    def test_delete_spot(self, client, spot, auth_headers):
        """Tests that a spot can be deleted."""
        response = client.delete(f"/spots/{spot.id}", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK

    def test_delete_spot_doesnt_exist(self, client, auth_headers):
        """Tests that a non-existent spot returns 404."""
        response = client.delete(f"/spots/{uuid4()}", headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_spots_by_bbox(self, client, spots):
        """Tests that all fixture spots are returned within a bounding box that contains them."""
        response = client.get("/spots/search/bbox", params={"min_lat": 50.0000, "max_lat": 55.0000,
                                                            "min_lng": -2.0000, "max_lng": 1.0000})
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        returned_ids = {s["id"] for s in data}
        expected_ids = {s["id"] for s in spots}

        assert returned_ids == expected_ids


class TestSpotImages:
    """Test class for /spots/{id}/images API endpoints."""

    test_image_dir = settings.BASE_DIR / "tests" / "test_images"

    def test_add_image(self, client, spot, auth_headers):
        """Tests uploading an image to a spot."""
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            response = client.post(f"/spots/{spot.id}/images", files={"file": f}, headers=auth_headers)
        assert response.status_code == HTTPStatus.CREATED
        assert "id" in response.json()

    def test_upload_image_wrong_type(self, client, spot, auth_headers):
        """Tests uploading an image to a spot with a wrong image type."""
        bad_image = self.test_image_dir / "test_spot.gif"
        response = client.post(f"/spots/{spot.id}/images",
                               files={"file": open(bad_image, "rb")}, headers=auth_headers)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_upload_image_too_large(self, client, spot, auth_headers):
        """Tests uploading an image that exceeds the size limit.
        Python doesn't complain that the file path doesn't exist here because we are just passing raw bytes as
        the file content"""
        large_file = b"0" * (MAX_FILE_SIZE + 1)
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            response = client.post(f"/spots/{spot.id}/images",
                                   files={"file": ("big.png", large_file, "image/png")}, headers=auth_headers)
        assert response.status_code == HTTPStatus.BAD_REQUEST


    def test_add_image_no_spot(self, client, auth_headers):
        """Tests that uploading to a non-existent spot returns 404."""
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            response = client.post(f"/spots/{uuid4()}/images", files={"file": f}, headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_image(self, client, spot, temp_upload_dir, auth_headers):
        """Tests deleting an image removes the DB record and file from disk."""
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            post_response = client.post(f"/spots/{spot.id}/images", files={"file": f}, headers=auth_headers)
        assert post_response.status_code == HTTPStatus.CREATED

        image_id = post_response.json()["id"]
        file_path = temp_upload_dir / str(spot.id) / "test_spot.png"
        assert file_path.exists()

        delete_response = client.delete(f"/spots/{spot.id}/images/{image_id}", headers=auth_headers)
        assert delete_response.status_code == HTTPStatus.OK
        assert not file_path.exists()

    def test_list_images(self, client, spot, auth_headers):
        """Tests that uploaded images are returned when listing a spot's images."""
        with open(self.test_image_dir / "test_spot.png", "rb") as f:
            response = client.post(f"/spots/{spot.id}/images", files={"file": f}, headers=auth_headers)
        assert response.status_code == HTTPStatus.CREATED

        with open(self.test_image_dir / "test_spot2.png", "rb") as f:
            response = client.post(f"/spots/{spot.id}/images", files={"file": f}, headers=auth_headers)
        assert response.status_code == HTTPStatus.CREATED

        response = client.get(f"/spots/{spot.id}/images")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 2
        filenames = {img["file_path"].replace("\\", "/").split("/")[-1] for img in data}
        assert "test_spot.png" in filenames
        assert "test_spot2.png" in filenames
