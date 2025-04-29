import builtins
import pandas as pd
import json
import pytest
from unittest import mock
from MovingItems import main

from MovingItems import (
    load_event_data,
    load_cv_data,
    extract_coordinates_from_excel,
    get_rfx_rfy_list,
    filter_and_clean_item_data,
    filter_by_coordinate_proximity
)

# ------------------------ Fixtures ------------------------
@pytest.fixture
def kafka_data():
    return load_event_data("kafkatopicdata.json")

@pytest.fixture
def cv_data():
    return load_cv_data("CVdata22.xlsx")

@pytest.fixture
def item_data():
    df = pd.read_csv("item_data_01.csv", dtype=str)
    return df.head(1000)

# ------------------------ Basic Load Tests ------------------------
def test_load_event_data(kafka_data):
    assert isinstance(kafka_data, list)
    assert all('global_id' in i for i in kafka_data)

def test_load_cv_data(cv_data):
    assert isinstance(cv_data, pd.DataFrame)
    assert "sng_did" in cv_data.columns
    assert "timestamp_coordinates" in cv_data.columns

# ------------------------ Coordinate Extraction Tests ------------------------
def test_extract_coordinates_success(cv_data, kafka_data):
    items = [i for i in kafka_data if i["Item_type"] == "unknown"][:3]
    rows, coords, cmap = extract_coordinates_from_excel(cv_data, items)
    assert isinstance(rows, list)
    assert isinstance(coords, list)
    assert isinstance(cmap, dict)

def test_extract_coordinates_malformed_data():
    df = pd.DataFrame([{
        "sng_did": "abc",
        "global_id": "gid",
        "timestamp_coordinates": "Not a list"
    }])
    item = {"sng_did": "abc", "global_id": "gid", "person_event_time": 123}
    rows, coords, cmap = extract_coordinates_from_excel(df, [item])
    assert len(rows) == 1  # row is added before parsing coords
    assert coords == []
    assert cmap == {}

def test_extract_coordinates_partial_valid_coords():
    coords = str([
        (123, "100", "100"),
        ("bad", "val", "val"),
        (123, 200, None)
    ])
    df = pd.DataFrame([{
        "sng_did": "abc",
        "global_id": "gid",
        "timestamp_coordinates": coords
    }])
    item = {"sng_did": "abc", "global_id": "gid", "person_event_time": 123}
    _, coords, cmap = extract_coordinates_from_excel(df, [item])
    assert len(coords) == 1
    assert "rfx" in cmap["gid"][0]

def test_extract_coordinates_no_matching_sngdid_or_gid(cv_data):
    item = {"sng_did": "nonexistent", "global_id": "nope", "person_event_time": 0}
    rows, coords, cmap = extract_coordinates_from_excel(cv_data, [item])
    assert rows == []
    assert coords == []
    assert cmap == {}

# ------------------------ RFX/RFY Extraction Tests ------------------------
def test_get_rfx_rfy_list(cv_data, kafka_data):
    items = [i for i in kafka_data if i["Item_type"] == "unknown"][:3]
    _, _, cmap = extract_coordinates_from_excel(cv_data, items)
    for gid in cmap:
        result = get_rfx_rfy_list(cmap, gid)
        assert isinstance(result, list)
        for p in result:
            assert "rfx" in p and "rfy" in p

def test_get_rfx_rfy_empty():
    cmap = {}
    assert get_rfx_rfy_list(cmap, "fake_id") == []

# ------------------------ Filtering Tests ------------------------
def test_filter_and_clean_item_data(item_data):
    cleaned = filter_and_clean_item_data(item_data.copy())
    assert not cleaned.empty
    assert "x" in cleaned.columns and "y" in cleaned.columns
    assert pd.api.types.is_numeric_dtype(cleaned["x"])

def test_filter_and_clean_all_invalid():
    df = pd.DataFrame({
        "events": ["Exit", "Departure"],
        "regionName": ["no match", "no match"],
        "x": ["bad", "bad"],
        "y": ["bad", "bad"]
    })
    cleaned = filter_and_clean_item_data(df)
    assert cleaned.empty

# ------------------------ Proximity Tests ------------------------
def test_filter_by_coordinate_proximity_match(cv_data, kafka_data, item_data):
    items = [i for i in kafka_data if i["Item_type"] == "unknown"][:3]
    _, _, cmap = extract_coordinates_from_excel(cv_data, items)
    coords = []
    for gid in cmap:
        coords.extend(get_rfx_rfy_list(cmap, gid))

    df = filter_and_clean_item_data(item_data.copy())
    filtered = filter_by_coordinate_proximity(df, coords, tolerance=100)
    assert isinstance(filtered, pd.DataFrame)

def test_filter_by_coordinate_proximity_empty_coords(item_data):
    df = filter_and_clean_item_data(item_data.copy())
    filtered = filter_by_coordinate_proximity(df, [])
    assert filtered.empty

# ------------------------ Batch/Chunk Integration Tests ------------------------
def test_batch_processing_coord_map_accumulation(cv_data, kafka_data):
    unknown_items = [i for i in kafka_data if i["Item_type"] == "unknown"]
    all_map = {}
    for i in range(0, len(unknown_items), 5):
        batch = unknown_items[i:i + 5]
        _, _, cmap = extract_coordinates_from_excel(cv_data, batch)
        for gid, coords in cmap.items():
            if gid not in all_map:
                all_map[gid] = []
            all_map[gid].extend(coords)
    assert isinstance(all_map, dict)

def test_csv_chunk_filtering(item_data, cv_data, kafka_data):
    items = [i for i in kafka_data if i["Item_type"] == "unknown"][:2]
    _, _, cmap = extract_coordinates_from_excel(cv_data, items)
    coords = []
    for gid in cmap:
        coords.extend(get_rfx_rfy_list(cmap, gid))
    cleaned = filter_and_clean_item_data(item_data.copy())
    result = filter_by_coordinate_proximity(cleaned, coords)
    assert isinstance(result, pd.DataFrame)
    
def test_main_function_with_mocked_dependencies():
    # Create mock JSON data
    mock_json_data = [
        {
            "Item_type": "unknown",
            "sng_did": "abc123",
            "global_id": "gid001",
            "person_event_time": 123456,
        }
    ]

    # Create mock CV Excel data
    mock_excel_df = pd.DataFrame([{
        "sng_did": "abc123",
        "global_id": "gid001",
        "timestamp_coordinates": str([[123456, 100.0, 200.0]])
    }])

    # Create mock item CSV chunk
    mock_item_df = pd.DataFrame([{
        "events": "Enter",
        "regionName": "apparel pad section",
        "x": 100,
        "y": 4760
    }])

    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_json_data))), \
         mock.patch("pandas.read_excel", return_value=mock_excel_df), \
         mock.patch("pandas.read_csv", return_value=iter([mock_item_df])), \
         mock.patch("builtins.print"):
        main()

