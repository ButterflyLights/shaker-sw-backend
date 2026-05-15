from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import json
import config
import measurement

app = FastAPI()

def process_measurement(text: str):
    measurement.run(text)

@app.post("/send")
async def receive_data(request: Request, background_tasks: BackgroundTasks):
    raw_data = await request.body()
    text = raw_data.decode("utf-8")

    print("Empfangen:")
    print(text)

    try:
        data = json.loads(text)
        if data["command"] == "start-measurement":
            if measurement.eventStartedPlayback.is_set() and not measurement.eventFinishedPlayback.is_set():
                print("still measuring!")
            
                return {
                    "status": "ok",
                    "message": "measurement ongoing"
                }

            else:
                background_tasks.add_task(process_measurement, text)

                return {
                    "status": "ok",
                    "message": "measurement started"
                }

        elif data["command"] == "stop-measurement":
            if measurement.eventStartedPlayback.is_set() and not measurement.eventFinishedPlayback.is_set():
                measurement.eventFinishedPlayback.set()
                return {
                    "status": "ok",
                    "message": "measurement stopped"
                }

            else:
                print("no measurement ongoing")
                return {
                    "status": "ok",
                    "message": "no measurement ongoing"
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