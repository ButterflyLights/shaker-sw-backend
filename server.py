from fastapi import FastAPI, Request
import uvicorn
import json
import config
import measurement

app = FastAPI()

@app.post("/send")
async def receive_data(request: Request):
    # Rohdaten als String lesen
    raw_data = await request.body()

    text = raw_data.decode("utf-8")

    print("Empfangener String:")
    print(text)

    # später als JSON interpretieren
    try:
        data = json.loads(text)

        print("JSON erfolgreich geparsed:")
        print(data)

        measurement.run(data)
        
        return {
            "status": "ok",
            "parsed": data
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Ungültiges JSON"
        }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.configData["backendHost"],
        port=config.configData["backendPort"]
    )