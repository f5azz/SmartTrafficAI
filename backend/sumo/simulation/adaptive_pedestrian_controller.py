import traci


# ============================================================
# CONFIGURATION
# ============================================================

TLS_ID = "center"

SIMULATION_END = 600

YELLOW_TIME = 3
ALL_RED_TIME = 1

MIN_PEDESTRIAN_WAITING = 2
PEDESTRIAN_GREEN_TIME = 10
PEDESTRIAN_COOLDOWN = 20

MIN_GREEN_TIME = 20
MAX_GREEN_TIME = 60


# ============================================================
# VEHICLE APPROACHES
# ============================================================

APPROACHES = {
    "NORTH": "north_to_center",
    "SOUTH": "south_to_center",
    "EAST": "east_to_center",
    "WEST": "west_to_center"
}


# ============================================================
# PEDESTRIAN CROSSINGS
# ============================================================

CROSSINGS = {
    "NORTH": ":center_c0",
    "EAST": ":center_c1",
    "SOUTH": ":center_c2",
    "WEST": ":center_c3"
}


# Confirmed pedestrian signal link indexes
PEDESTRIAN_LINKS = {
    "NORTH": 20,
    "EAST": 21,
    "SOUTH": 22,
    "WEST": 23
}


# ============================================================
# VEHICLE SIGNAL PHASES
# ============================================================

# Phase 0 = NORTH/SOUTH vehicle green
# Phase 1 = NORTH/SOUTH yellow
# Phase 2 = EAST/WEST vehicle green
# Phase 3 = EAST/WEST yellow

GROUP_PHASES = {
    "NS": 0,
    "EW": 2
}


# ============================================================
# VEHICLE ANALYSIS
# ============================================================

def get_vehicle_data():

    data = {}

    for direction, edge in APPROACHES.items():

        vehicles = traci.edge.getLastStepVehicleNumber(edge)

        queue = traci.edge.getLastStepHaltingNumber(edge)

        waiting = traci.edge.getWaitingTime(edge)

        score = (
            vehicles
            + queue * 2
            + waiting * 0.1
        )

        data[direction] = {
            "vehicles": vehicles,
            "queue": queue,
            "waiting": waiting,
            "score": score
        }

    return data


def get_congestion(vehicles):

    if vehicles <= 5:
        return "LOW"

    elif vehicles <= 10:
        return "MEDIUM"

    else:
        return "HIGH"


def calculate_green_time(score):

    green_time = int(20 + score * 2)

    green_time = max(
        MIN_GREEN_TIME,
        green_time
    )

    green_time = min(
        MAX_GREEN_TIME,
        green_time
    )

    return green_time


def choose_vehicle_direction(data):

    best_direction = max(
        data,
        key=lambda direction: data[direction]["score"]
    )

    best_score = data[best_direction]["score"]

    return best_direction, best_score


def direction_to_group(direction):

    if direction in ["NORTH", "SOUTH"]:
        return "NS"

    return "EW"


# ============================================================
# PEDESTRIAN ANALYSIS
# ============================================================

def get_pedestrian_data():

    waiting = {
        "NORTH": 0,
        "SOUTH": 0,
        "EAST": 0,
        "WEST": 0
    }

    waiting_time = {
        "NORTH": 0.0,
        "SOUTH": 0.0,
        "EAST": 0.0,
        "WEST": 0.0
    }

    crossing_to_direction = {
        crossing: direction
        for direction, crossing in CROSSINGS.items()
    }

    pedestrian_ids = traci.person.getIDList()

    for person_id in pedestrian_ids:

        next_edge = traci.person.getNextEdge(
            person_id
        )

        wait_time = traci.person.getWaitingTime(
            person_id
        )

        if (
            next_edge in crossing_to_direction
            and wait_time > 0
        ):

            direction = crossing_to_direction[next_edge]

            waiting[direction] += 1

            waiting_time[direction] += wait_time

    return waiting, waiting_time


def choose_pedestrian_group(waiting):

    ns_waiting = (
        waiting["NORTH"]
        + waiting["SOUTH"]
    )

    ew_waiting = (
        waiting["EAST"]
        + waiting["WEST"]
    )

    # NORTH + SOUTH
    if (
        ns_waiting >= MIN_PEDESTRIAN_WAITING
        and ns_waiting >= ew_waiting
    ):

        active = []

        if waiting["NORTH"] > 0:
            active.append("NORTH")

        if waiting["SOUTH"] > 0:
            active.append("SOUTH")

        return active

    # EAST + WEST
    if ew_waiting >= MIN_PEDESTRIAN_WAITING:

        active = []

        if waiting["EAST"] > 0:
            active.append("EAST")

        if waiting["WEST"] > 0:
            active.append("WEST")

        return active

    return []


def print_pedestrian_status(waiting, waiting_time):

    print("\n---------- PEDESTRIAN STATUS ----------")

    total = 0

    for direction in [
        "NORTH",
        "SOUTH",
        "EAST",
        "WEST"
    ]:

        count = waiting[direction]

        wait = waiting_time[direction]

        total += count

        print(
            f"{direction:<6} | "
            f"Waiting: {count:<3} | "
            f"Wait Time: {wait:>6.1f}s"
        )

    print("---------------------------------------")

    print(
        f"TOTAL PEDESTRIANS WAITING: {total}"
    )

    return total


# ============================================================
# UTILITY
# ============================================================

def run_steps(seconds):

    for _ in range(seconds):

        if traci.simulation.getTime() >= SIMULATION_END:
            return False

        traci.simulationStep()

    return True


def create_pedestrian_state(active_directions):

    state = ["r"] * 24

    for direction in active_directions:

        index = PEDESTRIAN_LINKS[direction]

        state[index] = "G"

    return "".join(state)


# ============================================================
# PEDESTRIAN PRIORITY
# ============================================================

def give_pedestrian_priority(active_directions):

    print("\n")
    print("================================================")
    print("       PEDESTRIAN PRIORITY ACTIVATED")
    print("================================================")

    print(
        "Requested crossings:",
        ", ".join(active_directions)
    )

    current_phase = traci.trafficlight.getPhase(
        TLS_ID
    )

    current_state = traci.trafficlight.getRedYellowGreenState(
        TLS_ID
    )

    print(
        "Current vehicle phase:",
        current_phase
    )

    # --------------------------------------------------------
    # Determine current vehicle phase
    # --------------------------------------------------------

    if current_phase == 0:

        yellow_phase = 1
        restore_phase = 0

        print(
            "Current traffic: NORTH/SOUTH GREEN"
        )

    elif current_phase == 2:

        yellow_phase = 3
        restore_phase = 2

        print(
            "Current traffic: EAST/WEST GREEN"
        )

    else:

        print(
            "Not currently in vehicle green."
        )

        print(
            "Pedestrian priority cancelled."
        )

        return False

    # --------------------------------------------------------
    # STEP 1 — Vehicle yellow
    # --------------------------------------------------------

    print("\nSTEP 1: Vehicle YELLOW")

    traci.trafficlight.setPhase(
        TLS_ID,
        yellow_phase
    )

    run_steps(YELLOW_TIME)

    # --------------------------------------------------------
    # STEP 2 — All red
    # --------------------------------------------------------

    print("STEP 2: ALL RED")

    all_red = "r" * len(current_state)

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        all_red
    )

    run_steps(ALL_RED_TIME)

    # --------------------------------------------------------
    # STEP 3 — Pedestrian green
    # --------------------------------------------------------

    pedestrian_state = create_pedestrian_state(
        active_directions
    )

    print("STEP 3: PEDESTRIAN GREEN")

    print(
        "Signal:",
        pedestrian_state
    )

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        pedestrian_state
    )

    print(
        f"Pedestrians crossing for "
        f"{PEDESTRIAN_GREEN_TIME} seconds..."
    )

    run_steps(
        PEDESTRIAN_GREEN_TIME
    )

    # --------------------------------------------------------
    # STEP 4 — Pedestrian clearance
    # --------------------------------------------------------

    print("STEP 4: PEDESTRIAN ALL RED")

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        all_red
    )

    run_steps(ALL_RED_TIME)

    # --------------------------------------------------------
    # STEP 5 — Restore normal signal program
    # --------------------------------------------------------

    print(
        "STEP 5: RESTORING VEHICLE SIGNAL"
    )

    traci.trafficlight.setProgram(
        TLS_ID,
        "0"
    )

    traci.trafficlight.setPhase(
        TLS_ID,
        restore_phase
    )

    print(
        "Restored vehicle phase:",
        restore_phase
    )

    print(
        "Pedestrian priority completed."
    )

    print("================================================")

    return True


# ============================================================
# VEHICLE GREEN
# ============================================================

def run_vehicle_green(direction, green_time):

    group = direction_to_group(direction)

    phase = GROUP_PHASES[group]

    print("\n")
    print("================================================")
    print("             ADAPTIVE VEHICLE CONTROL")
    print("================================================")

    print("AI Priority Direction:", direction)
    print("Signal Group:", group)
    print("Maximum Green Time:", green_time, "seconds")

    # Set normal traffic signal program
    traci.trafficlight.setProgram(TLS_ID, "0")

    # Set required vehicle phase
    traci.trafficlight.setPhase(TLS_ID, phase)

    # Instead of running the entire green time at once,
    # divide it into small decision intervals.
    remaining_time = green_time

    while remaining_time > 0:

        interval = min(5, remaining_time)

        print(
            f"\nRunning {group} green for "
            f"{interval} seconds..."
        )

        traci.trafficlight.setPhaseDuration(
            TLS_ID,
            interval
        )

        for _ in range(interval):

            if traci.simulation.getTime() >= SIMULATION_END:
                return False, False

            traci.simulationStep()

        remaining_time -= interval

        # ------------------------------------------------
        # Check pedestrians after every 5 seconds
        # ------------------------------------------------

        waiting, waiting_time = get_pedestrian_data()

        total_waiting = sum(waiting.values())

        print(
            "Pedestrians currently waiting:",
            total_waiting
        )

        # ------------------------------------------------
        # Give pedestrian priority immediately
        # when enough pedestrians are waiting.
        # ------------------------------------------------

        if total_waiting >= MIN_PEDESTRIAN_WAITING:

            active_directions = choose_pedestrian_group(
                waiting
            )

            if active_directions:

                print(
                    "\n>>> PEDESTRIAN DEMAND DETECTED "
                    "DURING VEHICLE GREEN <<<"
                )

                print(
                    "Crossings:",
                    ", ".join(active_directions)
                )

                return True, True

    # ----------------------------------------------------
    # Vehicle yellow transition
    # ----------------------------------------------------

    if phase == 0:
        yellow_phase = 1
    else:
        yellow_phase = 3

    print("\nVehicle green completed.")
    print("Changing to YELLOW.")

    traci.trafficlight.setPhase(
        TLS_ID,
        yellow_phase
    )

    run_steps(YELLOW_TIME)

    return True, False

def print_vehicle_status(data):

    print("\n---------- VEHICLE STATUS ----------")

    for direction in [
        "NORTH",
        "SOUTH",
        "EAST",
        "WEST"
    ]:

        values = data[direction]

        congestion = get_congestion(
            values["vehicles"]
        )

        print(
            f"{direction:<6} | "
            f"Vehicles: {values['vehicles']:<3} | "
            f"Queue: {values['queue']:<3} | "
            f"Waiting: {values['waiting']:>6.1f}s | "
            f"Score: {values['score']:>6.2f} | "
            f"{congestion}"
        )

    print("-----------------------------------")


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("================================================")
    print("     SMART TRAFFIC AI")
    print("     ADAPTIVE + PEDESTRIAN CONTROLLER")
    print("================================================")

    print(
        f"Simulation duration: {SIMULATION_END} seconds"
    )

    # IMPORTANT:
    # Use sumo first.
    # Once this works, we can change to sumo-gui.
    sumo_cmd = [
        "sumo",
        "-c",
        "pedestrian_test.sumocfg"
    ]

    traci.start(sumo_cmd)

    pedestrian_cooldown = 0

    try:

        while (
            traci.simulation.getTime()
            < SIMULATION_END
        ):

            current_time = traci.simulation.getTime()

            # ------------------------------------------------
            # Vehicle analysis
            # ------------------------------------------------

            vehicle_data = get_vehicle_data()

            print(
                f"\n\nSimulation Time: "
                f"{current_time:.0f}s"
            )

            print_vehicle_status(
                vehicle_data
            )

            # ------------------------------------------------
            # Pedestrian analysis
            # ------------------------------------------------

            waiting, waiting_time = (
                get_pedestrian_data()
            )

            print_pedestrian_status(
                waiting,
                waiting_time
            )

            # ------------------------------------------------
            # Cooldown
            # ------------------------------------------------

            if pedestrian_cooldown > 0:

                pedestrian_cooldown -= 1

            # ------------------------------------------------
            # Check pedestrian priority
            # ------------------------------------------------

            total_waiting = sum(
                waiting.values()
            )

            current_phase = (
                traci.trafficlight.getPhase(
                    TLS_ID
                )
            )

            vehicle_green = (
                current_phase in [0, 2]
            )

            if (
                total_waiting
                >= MIN_PEDESTRIAN_WAITING
                and vehicle_green
                and pedestrian_cooldown == 0
            ):

                active_directions = (
                    choose_pedestrian_group(
                        waiting
                    )
                )

                if active_directions:

                    print(
                        "\n>>> PEDESTRIAN DEMAND "
                        "DETECTED <<<"
                    )

                    success = (
                        give_pedestrian_priority(
                            active_directions
                        )
                    )

                    if success:

                        pedestrian_cooldown = (
                            PEDESTRIAN_COOLDOWN
                        )

                    continue

            # ------------------------------------------------
            # Adaptive vehicle decision
            # ------------------------------------------------

            best_direction, best_score = (
                choose_vehicle_direction(
                    vehicle_data
                )
            )

            green_time = calculate_green_time(
                best_score
            )

            print("\n>>> AI VEHICLE DECISION <<<")

            print(
                "Priority:",
                best_direction
            )

            print(
                "Score:",
                round(best_score, 2)
            )

            print(
                "Green time:",
                green_time,
                "seconds"
            )

            # ------------------------------------------------
            # Run selected vehicle phase
            # ------------------------------------------------

            success, pedestrian_requested = run_vehicle_green(best_direction,green_time)
            if not success:
                break
            if pedestrian_requested:
                waiting, waiting_time = get_pedestrian_data()
                active_directions = choose_pedestrian_group(
                    waiting
                    )
                if active_directions:
                    print("\n>>> INTERRUPTING VEHICLE PHASE <<<")
                    pedestrian_success = give_pedestrian_priority(
                        active_directions
                        )
                    if pedestrian_success:
                        pedestrian_cooldown = (
                            PEDESTRIAN_COOLDOWN
                            )

        # ----------------------------------------------------
        # FINAL RESULTS
        # ----------------------------------------------------

        print("\n")
        print("================================================")
        print("           SIMULATION COMPLETED")
        print("================================================")

        print(
            "Final simulation time:",
            traci.simulation.getTime()
        )

    finally:

        traci.close()

        print(
            "SUMO simulation closed."
        )


if __name__ == "__main__":

    main()