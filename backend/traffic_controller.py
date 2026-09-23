import traci

TLS_ID = "center"

# ==============================
# SETTINGS
# ==============================

DIRECTIONS = ["NORTH", "EAST", "SOUTH", "WEST"]

APPROACHES = {
    "NORTH": "north_to_center",
    "EAST": "east_to_center",
    "SOUTH": "south_to_center",
    "WEST": "west_to_center",
}

MIN_GREEN = 8
MAX_GREEN = 45
YELLOW_TIME = 3

# Your current traffic light has 24 controlled links:
# 0-4   = NORTH
# 5-9   = EAST
# 10-14 = SOUTH
# 15-19 = WEST
# 20-23 = pedestrian crossings

TOTAL_LINKS = 24

VEHICLE_LINKS = {
    "NORTH": range(0, 5),
    "EAST": range(5, 10),
    "SOUTH": range(10, 15),
    "WEST": range(15, 20),
}


# ==============================
# CONTROLLER STATE
# ==============================

current_direction_index = 0
current_direction = None

green_end_time = 0

emergency_active = False
emergency_direction = None

last_decision = {
    "priority_direction": "NORTH",
    "target_group": "NORTH",
    "current_group": "NORTH",
    "green_time": MIN_GREEN,
    "signal_switched": False,
    "emergency": False,
    "emergency_direction": None,
    "metrics": {},
}


# ==============================
# SIGNAL STATE GENERATOR
# ==============================

def make_signal_state(direction, color="G"):
    """
    Creates a 24-character SUMO traffic-light state.

    Only the requested direction is active.
    All other vehicle movements and pedestrian crossings are red.
    """

    state = ["r"] * TOTAL_LINKS

    if direction in VEHICLE_LINKS:
        for index in VEHICLE_LINKS[direction]:
            state[index] = color

    return "".join(state)


def set_green(direction):
    """Set one direction GREEN."""

    state = make_signal_state(direction, "G")

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        state
    )


def set_yellow(direction):
    """Set one direction YELLOW."""

    state = make_signal_state(direction, "y")

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        state
    )


def set_all_red():
    """Set complete intersection RED."""

    state = "r" * TOTAL_LINKS

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        state
    )


# ==============================
# TRAFFIC METRICS
# ==============================

def get_traffic_metrics():

    metrics = {}

    for direction, edge in APPROACHES.items():

        try:
            vehicles = traci.edge.getLastStepVehicleNumber(edge)

            queue = traci.edge.getLastStepHaltingNumber(edge)

            waiting_time = traci.edge.getWaitingTime(edge)

        except Exception:

            vehicles = 0
            queue = 0
            waiting_time = 0

        score = (
            vehicles
            + queue * 2
            + waiting_time * 0.1
        )

        metrics[direction] = {
            "vehicles": int(vehicles),
            "queue": int(queue),
            "waiting_time": round(waiting_time, 2),
            "score": round(score, 2),
        }

    return metrics


# ==============================
# GREEN TIME CALCULATION
# ==============================

def calculate_green_time(direction, metrics):

    data = metrics[direction]

    vehicles = data["vehicles"]
    queue = data["queue"]
    waiting = data["waiting_time"]

    demand = vehicles + queue

    # Base time
    green = 5 + (demand * 2)

    # Additional time for waiting vehicles
    if waiting > 10:
        green += 3

    if waiting > 20:
        green += 5

    green = max(MIN_GREEN, green)

    green = min(MAX_GREEN, green)

    return int(green)


# ==============================
# EMERGENCY DETECTION
# ==============================

def detect_emergency():

    try:

        vehicle_ids = traci.vehicle.getIDList()

        for vehicle_id in vehicle_ids:

            try:

                vehicle_type = traci.vehicle.getTypeID(
                    vehicle_id
                )

                if vehicle_type != "emergency":
                    continue

                road = traci.vehicle.getRoadID(
                    vehicle_id
                )

                # Emergency vehicle approaching
                for direction, edge in APPROACHES.items():

                    if road == edge:
                        return direction

                # Emergency vehicle is currently
                # inside the intersection.
                #
                # Keep its original approach priority.
                route = traci.vehicle.getRoute(
                    vehicle_id
                )

                if route:

                    first_edge = route[0]

                    for direction, edge in APPROACHES.items():

                        if first_edge == edge:

                            if road.startswith("center_to_"):
                                return direction

            except Exception:
                continue

    except Exception:
        pass

    return None


# ==============================
# START DIRECTION
# ==============================

def start_direction(direction, green_time):

    global current_direction
    global green_end_time

    current_direction = direction

    set_green(direction)

    current_time = traci.simulation.getTime()

    green_end_time = current_time + green_time


# ==============================
# SAFE DIRECTION SWITCH
# ==============================

def switch_direction(direction, green_time):

    global current_direction
    global green_end_time

    if current_direction == direction:

        # Already green.
        # Just extend/recalculate green.
        current_time = traci.simulation.getTime()

        green_end_time = current_time + green_time

        return False

    old_direction = current_direction

    # --------------------------
    # YELLOW
    # --------------------------

    if old_direction is not None:

        print(
            f"🟡 {old_direction} → YELLOW"
        )

        set_yellow(old_direction)

        for _ in range(YELLOW_TIME):

            traci.simulationStep()

    # --------------------------
    # ALL RED SAFETY
    # --------------------------

    set_all_red()

    traci.simulationStep()

    # --------------------------
    # NEW GREEN
    # --------------------------

    print(
        f"🟢 {direction} → GREEN"
    )

    start_direction(
        direction,
        green_time
    )

    return True


# ==============================
# NEXT CLOCKWISE DIRECTION
# ==============================

def get_next_direction(direction):

    if direction not in DIRECTIONS:
        return DIRECTIONS[0]

    index = DIRECTIONS.index(direction)

    return DIRECTIONS[
        (index + 1) % len(DIRECTIONS)
    ]


# ==============================
# FIND NEXT DIRECTION WITH TRAFFIC
# ==============================

def find_next_active_direction(
    current_direction,
    metrics
):

    if current_direction not in DIRECTIONS:

        current_direction = DIRECTIONS[-1]

    start_index = DIRECTIONS.index(
        current_direction
    )

    # Check clockwise
    for offset in range(1, len(DIRECTIONS) + 1):

        index = (
            start_index + offset
        ) % len(DIRECTIONS)

        direction = DIRECTIONS[index]

        data = metrics[direction]

        demand = (
            data["vehicles"]
            + data["queue"]
        )

        if demand > 0:

            return direction

    # Nobody waiting.
    return None


# ==============================
# EMERGENCY CONTROL
# ==============================

def handle_emergency(
    emergency_direction_value,
    metrics
):

    global emergency_active
    global emergency_direction

    emergency_active = True
    emergency_direction = emergency_direction_value

    print()
    print("=" * 65)
    print("🚨 EMERGENCY VEHICLE DETECTED")
    print("🚑 Priority Direction:", emergency_direction)
    print("=" * 65)

    # Give maximum green to emergency direction
    green_time = MAX_GREEN

    switched = switch_direction(
        emergency_direction,
        green_time
    )

    return {
        "priority_direction": emergency_direction,
        "target_group": emergency_direction,
        "current_group": current_direction,
        "green_time": green_time,
        "signal_switched": switched,
        "emergency": True,
        "emergency_direction": emergency_direction,
        "metrics": metrics,
    }


# ==============================
# NORMAL CLOCKWISE CONTROL
# ==============================

def handle_normal_traffic(metrics):

    global current_direction_index
    global current_direction
    global green_end_time
    global emergency_active
    global emergency_direction

    current_time = traci.simulation.getTime()

    # --------------------------
    # FIRST START
    # --------------------------

    if current_direction is None:

        direction = DIRECTIONS[0]

        green_time = calculate_green_time(
            direction,
            metrics
        )

        start_direction(
            direction,
            green_time
        )

        current_direction_index = 0

        print()
        print("=" * 60)
        print("🤖 ADAPTIVE TRAFFIC CONTROL")
        print("Direction:", direction)
        print("Vehicles:", metrics[direction]["vehicles"])
        print("Queue:", metrics[direction]["queue"])
        print("Waiting:", metrics[direction]["waiting_time"])
        print("Green Time:", green_time)
        print("=" * 60)

        return {
            "priority_direction": direction,
            "target_group": direction,
            "current_group": direction,
            "green_time": green_time,
            "signal_switched": False,
            "emergency": False,
            "emergency_direction": None,
            "metrics": metrics,
        }

    # --------------------------
    # CURRENT GREEN STILL ACTIVE
    # --------------------------

    if current_time < green_end_time:

        remaining = int(
            green_end_time - current_time
        )

        return {
            "priority_direction": current_direction,
            "target_group": current_direction,
            "current_group": current_direction,
            "green_time": remaining,
            "signal_switched": False,
            "emergency": False,
            "emergency_direction": None,
            "metrics": metrics,
        }

    # --------------------------
    # CURRENT DIRECTION FINISHED
    # --------------------------

    next_direction = find_next_active_direction(
        current_direction,
        metrics
    )

    # If no traffic anywhere,
    # continue clockwise with minimum green.
    if next_direction is None:

        next_direction = get_next_direction(
            current_direction
        )

    green_time = calculate_green_time(
        next_direction,
        metrics
    )

    switched = switch_direction(
        next_direction,
        green_time
    )

    current_direction_index = DIRECTIONS.index(
        next_direction
    )

    print()
    print("=" * 60)
    print("🤖 ADAPTIVE TRAFFIC DECISION")
    print("Direction:", next_direction)
    print(
        "Vehicles:",
        metrics[next_direction]["vehicles"]
    )
    print(
        "Queue:",
        metrics[next_direction]["queue"]
    )
    print(
        "Waiting:",
        metrics[next_direction]["waiting_time"]
    )
    print("Green Time:", green_time)
    print(
        "Next Direction:",
        get_next_direction(next_direction)
    )
    print("=" * 60)

    emergency_active = False
    emergency_direction = None

    return {
        "priority_direction": next_direction,
        "target_group": next_direction,
        "current_group": next_direction,
        "green_time": green_time,
        "signal_switched": switched,
        "emergency": False,
        "emergency_direction": None,
        "metrics": metrics,
    }


# ==============================
# MAIN CONTROLLER FUNCTION
# ==============================

def make_adaptive_decision(force=False):

    global last_decision
    global emergency_active
    global emergency_direction

    metrics = get_traffic_metrics()

    # --------------------------
    # EMERGENCY HAS HIGHEST PRIORITY
    # --------------------------

    detected_emergency = detect_emergency()

    if detected_emergency:

        decision = handle_emergency(
            detected_emergency,
            metrics
        )

        last_decision = decision

        return decision

    # --------------------------
    # NORMAL CLOCKWISE OPERATION
    # --------------------------

    decision = handle_normal_traffic(
        metrics
    )

    last_decision = decision

    return decision


# ==============================
# PUBLIC STATE HELPERS
# ==============================

def get_current_direction():

    return current_direction


def get_green_remaining():

    try:

        remaining = (
            green_end_time
            - traci.simulation.getTime()
        )

        return max(0, int(remaining))

    except Exception:

        return 0


def is_emergency_active():

    return emergency_active


def get_signal_state():

    try:

        return traci.trafficlight.getRedYellowGreenState(
            TLS_ID
        )

    except Exception:

        return "r" * TOTAL_LINKS