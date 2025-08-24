import csv
import io
from fastapi.responses import StreamingResponse

def list_of_dicts_to_csv(data: list) -> io.StringIO:
    output = io.StringIO()
    if not data:
        output.write("No data available.\n")
        output.seek(0)
        return output
    if hasattr(data[0], "dict"):
        data = [item.dict() for item in data]
    fieldnames = data[0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    output.seek(0)
    return output
