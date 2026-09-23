import os
import traci

from traffic_controller import (
    make_adaptive_decision,
    get_current_direction,
    get_green_remaining,
    is_emergency_active,
    get_signal_state,
)


# ============================================================
# SUMO CONFIGURATION
# ============================================================

SUMO_CONFIG = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "sumo",
        "simulation",
        "pedestrian_test.sumocfg",
    )
)

TLS_ID = "center"

SUMO_RUNNING = False


# ============================================================
# APPROACHES
# ============================================================

APPROACHES = {
    "NORTH": "north_to_center",
    "EAST": "east_to_center",
    "SOUTH": "south_to_center",
    "WEST": "west_to_center",
}


# ============================================================
# PEDESTRIAN CROSSINGS
# ============================================================

PEDESTRIAN_CROSSINGS = {
    "NORTH": ":center_c0",
    "EAST": ":center_c1",
    "SOUTH": ":center_c2",
    "WEST": ":center_c3",
}


# ============================================================
# START SUMO
# ============================================================

def start_sumo():

    global SUMO_RUNNING

    if SUMO_RUNNING:

        return

    if traci.isLoaded():

        SUMO_RUNNING = True

        return

    print()
    print("=" * 60)
    print("🚦 Starting SUMO...")
    print("=" * 60)

    traci.start(
        [
            "sumo",
            "-c",
            SUMO_CONFIG,
            "--start",
            "--quit-on-end",
        ]
    )

    SUMO_RUNNING = True

    print("✅ SUMO started successfully.")


# ============================================================
# STOP SUMO
# ============================================================

def stop_sumo():

    global SUMO_RUNNING

    if traci.isLoaded():

        try:

            traci.close()

        except Exception:
            pass

    SUMO_RUNNING = False

    print("🛑 SUMO stopped.")


# ============================================================
# SIMULATION STEP
# ============================================================

def simulation_step():

    if not SUMO_RUNNING:

        start_sumo()

    if not traci.isLoaded():

        return

    try:

        traci.simulationStep()

    except Exception as e:

        print(
            "SUMO simulation error:",
            e
        )


# ============================================================
# VEHICLE METRICS
# ============================================================

def get_vehicle_metrics():

    directions = {}

    for direction, edge in APPROACHES.items():

        try:

            vehicles = (
                traci.edge.getLastStepVehicleNumber(
                    edge
                )
            )

            queue = (
                traci.edge.getLastStepHaltingNumber(
                    edge
                )
            )

            waiting_time = (
                traci.edge.getWaitingTime(
                    edge
                )
            )

        except Exception:

            vehicles = 0
            queue = 0
            waiting_time = 0

        score = (
            vehicles
            + queue * 2
            + waiting_time * 0.1
        )

        # Traffic level
        if vehicles <= 5:

            status = "LOW"

        elif vehicles <= 10:

            status = "MEDIUM"

        else:

            status = "HIGH"

        directions[direction] = {

            "vehicles": int(
                vehicles
            ),

            "queue": int(
                queue
            ),

            "waiting_time": round(
                waiting_time,
                2
            ),

            "score": round(
                score,
                2
            ),

            "status": status,
        }

    return directions


# ============================================================
# PEDESTRIAN DATA
# ============================================================

def get_pedestrian_data():

    waiting = {
        "NORTH": 0,
        "EAST": 0,
        "SOUTH": 0,
        "WEST": 0,
    }

    crossing = {
        "NORTH": 0,
        "EAST": 0,
        "SOUTH": 0,
        "WEST": 0,
    }

    try:

        person_ids = (
            traci.person.getIDList()
        )

        for person_id in person_ids:

            try:

                road = traci.person.getRoadID(
                    person_id
                )

                for direction, crossing_id in (
                    PEDESTRIAN_CROSSINGS.items()
                ):

                    if road == crossing_id:

                        crossing[direction] += 1

                        break

            except Exception:

                continue

    except Exception:

        pass

    total_waiting = sum(
        waiting.values()
    )

    total_crossing = sum(
        crossing.values()
    )

    return {

        "total": (
            total_waiting
            + total_crossing
        ),

        "waiting": total_waiting,

        "crossing": total_crossing,

        "directions": {

            "NORTH": {
                "waiting": waiting["NORTH"],
                "crossing": crossing["NORTH"],
            },

            "EAST": {
                "waiting": waiting["EAST"],
                "crossing": crossing["EAST"],
            },

            "SOUTH": {
                "waiting": waiting["SOUTH"],
                "crossing": crossing["SOUTH"],
            },

            "WEST": {
                "waiting": waiting["WEST"],
                "crossing": crossing["WEST"],
            },
        },
    }


# ============================================================
# ACTIVE SIGNAL
# ============================================================

def get_active_signal():

    direction = get_current_direction()

    if direction is None:

        return "ALL RED"

    return direction


# ============================================================
# SIGNAL COLOR
# ============================================================

def get_signal_color():

    state = get_signal_state()

    if not state:

        return "RED"

    # Vehicle links for each direction
    groups = {

        "NORTH": state[0:5],

        "EAST": state[5:10],

        "SOUTH": state[10:15],

        "WEST": state[15:20],
    }

    direction = get_current_direction()

    if direction in groups:

        group = groups[direction]

        if "G" in group:

            return "GREEN"

        if "y" in group:

            return "YELLOW"

    return "RED"


# ============================================================
# GREEN TIME
# ============================================================

def get_green_time():

    return get_green_remaining()


# ============================================================
# OVERALL TRAFFIC STATUS
# ============================================================

def get_overall_traffic_status(
    directions
):

    total_vehicles = sum(
        item["vehicles"]
        for item in directions.values()
    )

    if total_vehicles <= 20:

        return "LOW"

    if total_vehicles <= 50:

        return "MEDIUM"

    return "HIGH"


# ============================================================
# TOTAL VEHICLES
# ============================================================

def get_total_vehicle_count(
    directions
):

    return sum(
        item["vehicles"]
        for item in directions.values()
    )


# ============================================================
# TRAFFIC DATA
# ============================================================

def get_traffic_data():

    if not SUMO_RUNNING:

        start_sumo()

    # Advance simulation
    simulation_step()

    # Run adaptive controller
    decision = make_adaptive_decision()

    # Get traffic information
    directions = get_vehicle_metrics()

    # Pedestrian information
    pedestrians = get_pedestrian_data()

    # Total vehicles
    total_vehicles = (
        get_total_vehicle_count(
            directions
        )
    )

    # Current signal
    active_signal = get_active_signal()

    # Signal color
    signal_color = get_signal_color()

    # Green remaining
    green_time = get_green_time()

    # Overall traffic
    traffic_status = (
        get_overall_traffic_status(
            directions
        )
    )

    # Current simulation time
    try:

        simulation_time = (
            traci.simulation.getTime()
        )

    except Exception:

        simulation_time = 0

    # Emergency
    emergency = is_emergency_active()

    # ========================================================
    # API RESPONSE
    # ========================================================

    return {

        # Simulation
        "simulation_time": round(
            simulation_time,
            1
        ),

        # Vehicles
        "vehicles_detected": total_vehicles,

        # Pedestrians
        "pedestrians_detected":
            pedestrians["total"],

        "pedestrians_waiting":
            pedestrians["waiting"],

        "pedestrians_crossing":
            pedestrians["crossing"],

        "pedestrian_directions":
            pedestrians["directions"],

        # Signal
        "active_signal":
            active_signal,

        "signal_color":
            signal_color,

        "priority_direction":
            decision[
                "priority_direction"
            ],

        "green_time":
            green_time,

        # Traffic
        "traffic_status":
            traffic_status,

        # Controller
        "control_mode":
            "ADAPTIVE AI",

        "signal_switched":
            decision[
                "signal_switched"
            ],

        # Emergency
        "emergency":
            emergency,

        "emergency_direction":
            decision[
                "emergency_direction"
            ],

        # Signal state
        "signal_state":
            get_signal_state(),

        # Direction information
        "directions":
            directions,
    }