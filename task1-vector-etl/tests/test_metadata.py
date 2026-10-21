from pathlib import Path
import pytest
from etl.metadata import build_metadata

def test_requires_tenant_and_access_tier(tmp_path):
    f = tmp_path / "sample.md"
    f.write_text("hello")
    with pytest.raises(ValueError):
        build_metadata(f, {}, tmp_path, {})
