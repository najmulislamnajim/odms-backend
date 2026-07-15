from app.sync.base_sync import bulk_upsert, fetch_from_sap

MATERIAL_COLUMN_MAP = {
    "MATNR": "material_id",
    "MaterialName": "material_name",
    "Plant": "plant_code",
    "SalesOrg": "sales_org",
    "DisChannel": "distribution_channel",
    "ProducerCompany": "producer_company",
    "Team1": "team",
    "PackSize": "pack_size",
    "UnitTP": "unit_tp",
    "UnitVAT": "unit_vat",
    "MRP": "mrp",
    "BrandName": "brand_name",
    "BrandDescription": "brand_description",
    "Active": "active",
}

TARGET_COLUMNS = list(MATERIAL_COLUMN_MAP.values())
CONFLICT_COLUMNS = ["material_id"]   # material_id primary key, tai ei diye conflict


def _clean(row: dict) -> dict:
    # SAP 'active' varchar → Boolean (X/1/true → True, baki False)
    val = (row.get("active") or "").strip().upper()
    row["active"] = val in ("Y", "y", "X", "1", "TRUE", "ACTIVE")
    return row


def sync_material() -> int:
    rows = fetch_from_sap(
        sap_table="Material",
        column_map=MATERIAL_COLUMN_MAP,
    )
    return bulk_upsert(
        target_table="rpl_material_list",
        target_columns=TARGET_COLUMNS,
        conflict_columns=CONFLICT_COLUMNS,
        rows=rows,
        transform=_clean,
    )