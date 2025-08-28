from ..s3_client import s3_client


def test_import_s3_client():
    assert s3_client is not None
