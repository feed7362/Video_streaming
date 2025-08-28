from convertor.s3_client import s3_client


def test_import_s3_client() -> None:
    assert s3_client is not None
