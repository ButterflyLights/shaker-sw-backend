from fastapi import FastAPI, Request
import uvicorn
import threading
import config
import measurement

app = FastAPI()

measurement_lock = threading.Lock()

def process_measurement(data):
    measurement.run(data)

@app.post("/send")
async def receive_data(request: Request):

    try:
        data = await request.json()
        command = data.get("command")

        if command == "start-measurement":
            with measurement_lock:
                if measurement.getState() == measurement.MeasurementState.RUNNING:
                    print("still measuring!")

                    return {
                        "status": "ok",
                        "message": "measurement ongoing"
                    }

                threading.Thread(
                    target=process_measurement,
                    args=(data,),
                    daemon=True
                ).start()

                return {
                    "status": "ok",
                    "message": "measurement started"
                }

        elif command == "stop-measurement":
            if measurement.getState() == measurement.MeasurementState.RUNNING:
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

        return {
            "status": "error",
            "message": "unknown command"
        }

    except Exception as e:

        print(e)

        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":

    uvicorn.run(
        app,
        host=config.configData["backendHost"],
        port=config.configData["backendPort"]
    )