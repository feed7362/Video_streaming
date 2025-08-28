from convertor.config import S3Settings, get_s3_settings


def test_import_config() -> None:
    assert isinstance(get_s3_settings, S3Settings)
