from app.sync.customer_sync import _clean


def test_clean_shop_name_joins_name1_name2():
    row = {
        "name1": "Hazi Pharmacy",
        "name2": "and Store",
        "street": "Main Road", "street1": "", "street2": "", "street3": "",
        "trans_p_zone": "0000400117",
    }
    result = _clean(row)
    assert result["shop_name"] == "Hazi Pharmacy and Store"


def test_clean_shop_name_only_name1_when_name2_empty():
    row = {
        "name1": "Hazi Pharmacy",
        "name2": "",
        "street": "", "street1": "", "street2": "", "street3": "",
        "trans_p_zone": "0000400117",
    }
    result = _clean(row)
    assert result["shop_name"] == "Hazi Pharmacy"


def test_clean_route_code_strips_leading_zeros():
    row = {
        "name1": "Shop", "name2": "",
        "street": "", "street1": "", "street2": "", "street3": "",
        "trans_p_zone": "0000400117",
    }
    result = _clean(row)
    assert result["route_code"] == "400117"


def test_clean_street_joins_all_parts():
    row = {
        "name1": "Shop", "name2": "",
        "street": "House 5", "street1": "Road 3", "street2": "", "street3": "Dhaka",
        "trans_p_zone": "0000400117",
    }
    result = _clean(row)
    assert result["street"] == "House 5, Road 3, Dhaka"


def test_clean_sets_active_true():
    row = {
        "name1": "Shop", "name2": "",
        "street": "", "street1": "", "street2": "", "street3": "",
        "trans_p_zone": "0000400117",
    }
    result = _clean(row)
    assert result["active"] is True
    
def test_clean_route_code_none_when_empty():
    row = {
        "name1": "Shop", "name2": "",
        "street": "", "street1": "", "street2": "", "street3": "",
        "trans_p_zone": "",
    }
    result = _clean(row)
    assert result["route_code"] is None