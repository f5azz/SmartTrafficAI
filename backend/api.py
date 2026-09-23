from yolo_service import yolo_service
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sumo_service import (
    get_traffic_data,
    start_sumo,
    stop_sumo
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(

    title="Smart Traffic AI API",

    description="AI Adaptive Traffic Control System",

    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    print("Starting Smart Traffic AI backend...")

    start_sumo()

    print("Starting YOLO vision system...")

    yolo_service.start()


# ============================================================
# SHUTDOWN
# ============================================================

@app.on_event("shutdown")
def shutdown_event():

    print("Stopping SUMO...")

    stop_sumo()


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "system": "Smart Traffic AI",

        "status": "online",

        "message":
            "AI Adaptive Traffic Control API is running"
    }


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.get("/system-status")
def system_status():

    return {

        "fastapi": "ONLINE",

        "ai_engine": "ACTIVE",

        "sumo": "CONNECTED",

        "yolo": "READY"
    }


# ============================================================
# TRAFFIC STATUS
# ============================================================

@app.get("/traffic-status")
def traffic_status():

    try:

        return get_traffic_data()

    except Exception as e:

        return {

            "status": "ERROR",

            "message": str(e)
        }
@app.get("/camera-status")
def camera_status():

    yolo = yolo_service.get_status()

    return {
        "system": "YOLO Vision",
        "status": yolo["status"],

        "cameras": {
            "NORTH": {
                "status": yolo["status"],
                "vehicles": yolo["vehicles"],
                "density": yolo["density"],
                "car": yolo["car"],
                "motorcycle": yolo["motorcycle"],
                "bus": yolo["bus"],
                "truck": yolo["truck"],
                "fps": yolo["fps"],
            },

            "EAST": {
                "status": "READY",
                "vehicles": 0,
                "density": "NO FEED",
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
                "fps": 0,
            },

            "SOUTH": {
                "status": "READY",
                "vehicles": 0,
                "density": "NO FEED",
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
                "fps": 0,
            },

            "WEST": {
                "status": "READY",
                "vehicles": 0,
                "density": "NO FEED",
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
                "fps": 0,
            },
        }
    }
    