import json
import pandas as pd
import ast


def load_event_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_cv_data(excel_path):
    return pd.read_excel(excel_path, dtype=str)


def extract_coordinates_from_excel(excel_df, unknown_items):
    matched_rows = []
    matched_coords = []
    coord_map = {}

    for item in unknown_items:
        sng_did = item.get("sng_did")
        global_id = item.get("global_id")
        person_event_time = item.get("person_event_time")

        filtered = excel_df[
            (excel_df["sng_did"] == sng_did) &
            (excel_df["global_id"] == global_id)
        ]

        for _, row in filtered.iterrows():
            matched_rows.append(row.to_dict())
            coords_raw = row.get("timestamp_coordinates")

            if not coords_raw or not coords_raw.strip().startswith("[") or not coords_raw.strip().endswith("]"):
                continue

            try:
                parsed_coords = ast.literal_eval(coords_raw)
                if not isinstance(parsed_coords, list):
                    continue

                valid_coords = [
                    coord for coord in parsed_coords
                    if isinstance(coord, (list, tuple)) and len(coord) == 3
                ]

                for coord in valid_coords:
                    timevalue, x, y = coord
                    if timevalue == person_event_time:
                        try:
                            x = int(float(x))
                            y = int(float(y))
                            rfx = 4960 - x
                            rfy = 4960 - y

                            matched_coords.append({"x": x, "y": y})

                            if global_id not in coord_map:
                                coord_map[global_id] = []

                            coord_map[global_id].append({
                                "person_event_time": person_event_time,
                                "x": x,
                                "y": y,
                                "rfx": rfx,
                                "rfy": rfy
                            })

                        except Exception:
                            continue

            except (SyntaxError, ValueError):
                continue

    return matched_rows, matched_coords, coord_map


def get_rfx_rfy_list(coord_map, global_id):
    return [{"rfx": entry["rfx"], "rfy": entry["rfy"]}
            for entry in coord_map.get(global_id, [])]


def load_and_filter_item_data(csv_path):
    df = pd.read_csv(csv_path)

    # Filter unwanted events
    df = df[~df["events"].isin(["Departure", "Exit"])]

    # Filter regionName for "apparel pad"
    df = df[df["regionName"].str.contains("apparel pad", case=False, na=False)]

    # Convert and clean x/y
    df["x"] = pd.to_numeric(df["x"], errors='coerce')
    df["y"] = pd.to_numeric(df["y"], errors='coerce')
    df = df.dropna(subset=["x", "y"])

    return df


def filter_by_coordinate_proximity(df, rfx_rfy_list, tolerance=50):
    def is_within_range(row):
        return any(
            abs(row["x"] - ref["rfx"]) <= tolerance and abs(row["y"] - ref["rfy"]) <= tolerance
            for ref in rfx_rfy_list
        )

    return df[df.apply(is_within_range, axis=1)]


def main():
    kafkatopicjson_file = "kafkatopicdata.json"
    cvdataexcel_file = "CVdata22.xlsx"
    itemcoreserver_file = "item_data.csv"

    # Load data
    kafkaeventjson_data = load_event_data(kafkatopicjson_file)
    cvdata_df = load_cv_data(cvdataexcel_file)

    # Process coordinates
    unknown_items = [item for item in kafkaeventjson_data if item.get("Item_type") == "unknown"]
    matched_rows, matched_coords, global_id_coord_map = extract_coordinates_from_excel(cvdata_df, unknown_items)

    # Debug prints (optional)
    print("\nFinal Dictionary (global_id -> list of {person_event_time, x, y, rfx, rfy}):")
    for gid, coords in global_id_coord_map.items():
        print(f"{gid}:")
        for c in coords:
            print(f"  {c}")

    # Combine rfx/rfy list for all global_ids
    rfx_rfy_list = []
    for gid in global_id_coord_map:
        rfx_rfy_list.extend(get_rfx_rfy_list(global_id_coord_map, gid))

    print("\nCombined RFX/RFY list for all global_ids:")
    print(rfx_rfy_list)

    # Load and filter item data
    filtered_coreserver_item_df = load_and_filter_item_data(itemcoreserver_file)

    # Match based on coordinates
    matching_rows = filter_by_coordinate_proximity(filtered_coreserver_item_df, rfx_rfy_list)

    print("\nFiltered Moving Item Data:")
    print(matching_rows)


if __name__ == "__main__":
    main()
