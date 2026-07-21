import pytest

from app.sync.material_sync import _clean


@pytest.mark.parametrize("sap_value, expected", [
    ("X", True),
    ("1", True),
    ("Y", True),
    ("x", True),
    ("y", True),
    ("", False),
    ("0", False),
    ("N", False),
    (None, False),
])
def test_clean_active_conversion(sap_value, expected):
    """SAP active-value → Boolean (sob case)."""
    result = _clean({"active": sap_value})
    assert result["active"] is expected