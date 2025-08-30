import pytest

from ..main import cleanup_dirs, prepare_dirs


@pytest.mark.asyncio
async def test_prepare_and_cleanup_dirs() -> None:
    vid = "testvid"
    path = await prepare_dirs(vid)
    assert path.exists()
    cleanup_dirs(vid)
    assert not path.exists()
