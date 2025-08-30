import os
from datetime import datetime
from io import BytesIO

from PIL import Image  # type: ignore

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user_schema import UserCreateSchema
from app.repositories.user_repo import UserRepository

from . import pytest, pytestmark


class TestMiscRoute:
    @pytest.fixture(autouse=True)
    def init(self, client, api_prefix, db_session, payload_user_register, payload_user_login):
        self.client = client
        self.api_prefix = api_prefix
        self.db_session = db_session
        self.payload_user_register = payload_user_register
        self.payload_user_login = payload_user_login
        self.upload_url = f"{self.api_prefix}/upload/"

    @pytest.fixture(autouse=True)
    async def setup_user(self):
        # create user
        user = await UserRepository(self.db_session).create(UserCreateSchema(**self.payload_user_register))
        assert "id" in user.model_dump()

        # update user role to Admin, verified, status
        user.is_verified = True
        user.verified_at = datetime.now()
        user.profile.status_id = settings.STATUS_USER_ACTIVE

        # update user
        await UserRepository(self.db_session).add_one(user)
        assert user.is_verified == True
        assert user.profile.status_id == settings.STATUS_USER_ACTIVE

        self.user = user

        # generate access_token
        access_token = await create_access_token(
            user_data={"email": self.user.email, "user_id": str(self.user.id)},
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        self.headers = headers

    async def test_upload_image(self):
        root_dir = os.path.abspath(".")
        file_path = os.path.join(root_dir, f"static/images/img-1920.png")
        if os.path.isfile(file_path):
            _files = {"file": open(file_path, 'rb')}

        # request upload image
        url = f"{self.upload_url}image"
        response = await self.client.post(url, headers=self.headers, files=_files)
        data = response.json()
        # print(data)

        assert response.status_code == 200
        assert "file_name" in data

        # medium image
        root_dir = os.path.abspath(".")
        file_path = os.path.join(root_dir, f"static/images/avatar-md.jpg")
        if os.path.isfile(file_path):
            _files = {"file": open(file_path, 'rb')}

        # request upload medium image
        url = f"{self.upload_url}image"
        response = await self.client.post(url, headers=self.headers, files=_files)
        data = response.json()
        # print(data)

        assert response.status_code == 200
        assert "file_name" in data

        # small image
        file_path = os.path.join(root_dir, f"static/images/avatar-sm.jpg")
        if os.path.isfile(file_path):
            _files = {"file": open(file_path, 'rb')}

        # request upload small image
        url = f"{self.upload_url}image"
        response = await self.client.post(url, headers=self.headers, files=_files)
        data = response.json()
        # print(data)

        assert response.status_code == 200
        assert "file_name" in data

    async def test_upload_image_failed(self):
        root_dir = os.path.abspath(".")
        file_path = os.path.join(root_dir, f"tests/data/test_file.pdf")
        if os.path.isfile(file_path):
            _files = {"file": open(file_path, 'rb')}

        # request upload image
        url = f"{self.upload_url}image"
        response = await self.client.post(url, headers=self.headers, files=_files)
        data = response.json()
        # print(data)

        assert response.status_code == 500
        assert data["detail"] == "Please make sure the file is an image file"

    async def test_upload_files(self):
        # image type
        root_dir = os.path.abspath(".")
        file_path = os.path.join(root_dir, f"static/images/img-1920.png")
        if os.path.isfile(file_path):
            _files = {"file": open(file_path, 'rb')}

        # request upload image
        url = f"{self.upload_url}file"
        response = await self.client.post(url, headers=self.headers, files=_files)
        data = response.json()
        # print(data)

        assert response.status_code == 200
        assert "file_name" in data

        # pdf file type
        root_dir = os.path.abspath(".")
        file_path = os.path.join(root_dir, f"static/files/pdf_file.pdf")
        if os.path.isfile(file_path):
            _files = {"file": open(file_path, 'rb')}

        # request upload file
        url = f"{self.upload_url}file"
        response = await self.client.post(url, headers=self.headers, files=_files)
        data = response.json()
        # print(data)

        assert response.status_code == 200
        assert "file_name" in data

        # doc file type
        file_path = os.path.join(root_dir, f"static/files/doc_file.docx")
        if os.path.isfile(file_path):
            _files = {"file": open(file_path, 'rb')}

        # request upload doc file
        url = f"{self.upload_url}file"
        response = await self.client.post(url, headers=self.headers, files=_files)
        data = response.json()
        # print(data)

        assert response.status_code == 200
        assert "file_name" in data

    async def test_upload_too_large(self):
        url = f"{self.upload_url}file"

        # Simulasikan file lebih dari 5MB
        large_file = b"x" * (30 * 1024 * 1024 + 1)
        response = await self.client.post(
            url,
            headers=self.headers,
            files={"file": ("large.jpg", large_file, "image/jpeg")},
        )
        assert response.status_code == 500
        assert "File size exceeds" in response.json()["detail"]

    async def test_upload_corrupted_image(self):
        url = f"{self.upload_url}file"

        corrupted_image = b"thisisnotanimage"
        response = await self.client.post(
            url,
            headers=self.headers,
            files={"file": ("broken.jpg", corrupted_image, "image/jpeg")},
        )
        # print(response.json())
        assert response.status_code == 500
        assert "cannot identify image file" in response.json()["detail"]
