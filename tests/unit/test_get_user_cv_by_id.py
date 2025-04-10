import pytest
from fastapi import HTTPException
from helpers.cv import get_user_cv_by_id


class DummyCV:
    def __init__(self, id, content):
        self.id = id
        self.content = content


class DummyUser:
    def __init__(self, cvs):
        self.cvs = cvs


def test_get_user_cv_by_id_success():
    cv1 = DummyCV(id=1, content="CV 1")
    cv2 = DummyCV(id=2, content="CV 2")
    user = DummyUser(cvs=[cv1, cv2])

    result = get_user_cv_by_id(user, 2)

    assert result == cv2
    assert result.content == "CV 2"


def test_get_user_cv_by_id_not_found():
    cv1 = DummyCV(id=1, content="CV 1")
    user = DummyUser(cvs=[cv1])

    with pytest.raises(HTTPException) as exc_info:
        get_user_cv_by_id(user, 999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "CV not found"
