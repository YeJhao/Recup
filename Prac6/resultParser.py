import json
from pathlib import Path

# Asocia cada fichero de respuesta con su prefijo
INFO_NEED = {
    "respuesta_1.json": "101-4",
    "respuesta_2.json": "106-4",
    "respuesta_3.json": "206-4",
    "respuesta_4.json": "209-2",
    "respuesta_5.json": "305-4",
}

OUTPUT = "results.txt"

with open(OUTPUT, "w", encoding="utf-8") as out:
    for filename, prefix in INFO_NEED.items():
        with open(Path("respuesta") / filename, encoding="utf-8") as f:
            data = json.load(f)

        for doc in data["response"]["docs"]:
            id = doc["id"].split("_")[-1].replace(".xml", "")
            out.write(f"{prefix}\thttp://zaguan.unizar.es/record/{id}\n")
