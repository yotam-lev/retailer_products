import csv
import math
from typing import List, Dict, Any

class Sorter:
    ORIGIN = (-33.761, 151.129)

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def process_and_sort_csv(input_filepath: str, output_filepath: str):
        with open(input_filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        processed = []
        for row in data:
            try:
                lat = float(row['lat'])
                lng = float(row['lng'])
                row['distance_km'] = Sorter.haversine(Sorter.ORIGIN[0], Sorter.ORIGIN[1], lat, lng)
                processed.append(row)
            except (ValueError, TypeError, KeyError):
                continue

        processed.sort(key=lambda x: x['distance_km'])

        fieldnames = reader.fieldnames + ['distance_km']
        with open(output_filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed)
