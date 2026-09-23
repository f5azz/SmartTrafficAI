import traci


# ============================================================
# CONFIGURATION
# ============================================================

TLS_ID = "center"

SIMULATION_END = 600

YELLOW_TIME = 3
ALL_RED_TIME = 1
PEDESTRIAN_GREEN_TIME = 10

# Minimum number of waiting pedestrians
# required before requesting priority
MIN_WAITING = 2

# Prevent repeated requests
COOLDOWN = 20


# ============================================================
# PEDESTRIAN CROSSINGS
# ============================================================

CROSSINGS = {
    "NORTH": ":center_c0",
    "EAST": ":center_c1",
    "SOUTH": ":center_c2",
    "WEST": ":center_c3"
}


# ============================================================
# CONFIRMED PEDESTRIAN SIGNAL LINK INDICES
#
# Obtained from check_ped_links.py
# ============================================================

PEDESTRIAN_LINKS = {
    "NORTH": 20,
    "EAST": 21,
    "SOUTH": 22,
    "WEST": 23
}


# ============================================================
# GET PEDESTRIAN DATA
# ============================================================

def get_pedestrian_data():

    waiting = {
        "NORTH": 0,
        "EAST": 0,
        "SOUTH": 0,
        "WEST": 0
    }

    waiting_time = {
        "NORTH": 0.0,
        "EAST": 0.0,
        "SOUTH": 0.0,
        "WEST": 0.0
    }

    crossing_to_direction = {
        crossing: direction
        for direction, crossing in CROSSINGS.items()
    }

    for person_id in traci.person.getIDList():

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

            direction = crossing_to_direction[
                next_edge
            ]

            waiting[direction] += 1

            waiting_time[direction] += wait_time

    return waiting, waiting_time


# ============================================================
# PEDESTRIAN DEMAND
# ============================================================

def get_demand(count):

    if count >= 5:
        return "HIGH"

    elif count >= 2:
        return "MEDIUM"

    elif count == 1:
        return "LOW"

    return "NONE"


# ============================================================
# PRINT PEDESTRIAN STATUS
# ============================================================

def print_status(waiting, waiting_time):

    print(
        "\n========== PEDESTRIAN STATUS =========="
    )

    total = 0

    for direction in CROSSINGS:

        count = waiting[direction]

        wait = waiting_time[direction]

        total += count

        print(
            f"{direction:<6} | "
            f"Waiting: {count:<3} | "
            f"Wait Time: {wait:>6.1f}s | "
            f"Demand: {get_demand(count)}"
        )

    print("---------------------------------------")

    print(
        f"TOTAL WAITING: {total}"
    )

    print(
        "======================================="
    )

    return total


# ============================================================
# CHOOSE PEDESTRIAN GROUP
#
# NORTH + SOUTH are handled together.
# EAST + WEST are handled together.
# ============================================================

def choose_pedestrian_group(waiting):

    ns_waiting = (
        waiting["NORTH"]
        + waiting["SOUTH"]
    )

    ew_waiting = (
        waiting["EAST"]
        + waiting["WEST"]
    )

    # --------------------------------------------------------
    # NORTH / SOUTH
    # --------------------------------------------------------

    if (
        ns_waiting >= MIN_WAITING
        and ns_waiting >= ew_waiting
    ):

        active = []

        if waiting["NORTH"] > 0:
            active.append("NORTH")

        if waiting["SOUTH"] > 0:
            active.append("SOUTH")

        return active

    # --------------------------------------------------------
    # EAST / WEST
    # --------------------------------------------------------

    if ew_waiting >= MIN_WAITING:

        active = []

        if waiting["EAST"] > 0:
            active.append("EAST")

        if waiting["WEST"] > 0:
            active.append("WEST")

        return active

    return []


# ============================================================
# RUN SIMULATION STEPS
# ============================================================

def run_steps(seconds):

    for _ in range(seconds):

        current_time = traci.simulation.getTime()

        if current_time >= SIMULATION_END:
            return

        traci.simulationStep()


# ============================================================
# CREATE PEDESTRIAN GREEN SIGNAL
# ============================================================

def create_pedestrian_state(active_directions):

    # There are 24 controlled links.
    # Start with everything RED.

    state = ["r"] * 24

    for direction in active_directions:

        index = PEDESTRIAN_LINKS[direction]

        state[index] = "G"

    return "".join(state)


# ============================================================
# GIVE PEDESTRIAN PRIORITY
# ============================================================

def give_pedestrian_priority(active_directions):

    print("\n")
    print(
        "################################################"
    )
    print(
        "#       PEDESTRIAN PRIORITY REQUEST            #"
    )
    print(
        "################################################"
    )

    print(
        "Requested crossings:",
        ", ".join(active_directions)
    )

    # --------------------------------------------------------
    # READ CURRENT SIGNAL
    # --------------------------------------------------------

    current_phase = traci.trafficlight.getPhase(
        TLS_ID
    )

    current_state = (
        traci.trafficlight.getRedYellowGreenState(
            TLS_ID
        )
    )

    print(
        f"Current phase        : {current_phase}"
    )

    print(
        f"Current signal state : {current_state}"
    )

    # --------------------------------------------------------
    # RESTORE NORMAL PROGRAM IF NECESSARY
    #
    # setRedYellowGreenState() puts SUMO into a custom
    # signal-state mode. Restore program 0 before trying
    # to access phases 0, 1, 2, 3 again.
    # --------------------------------------------------------

    if current_state == "r" * len(current_state):

        print(
            "Signal is currently in custom all-red state."
        )

        print(
            "Restoring normal traffic signal program 0..."
        )

        traci.trafficlight.setProgram(
            TLS_ID,
            "0"
        )

        current_phase = (
            traci.trafficlight.getPhase(
                TLS_ID
            )
        )

        current_state = (
            traci.trafficlight.getRedYellowGreenState(
                TLS_ID
            )
        )

        print(
            f"Restored phase        : {current_phase}"
        )

        print(
            f"Restored signal state : {current_state}"
        )

    # --------------------------------------------------------
    # DETERMINE CURRENT VEHICLE GREEN
    # --------------------------------------------------------

    if current_phase == 0:

        print(
            "Vehicle traffic      : NORTH/SOUTH GREEN"
        )

        yellow_phase = 1

        restore_phase = 0

    elif current_phase == 2:

        print(
            "Vehicle traffic      : EAST/WEST GREEN"
        )

        yellow_phase = 3

        restore_phase = 2

    else:

        print(
            "Current phase is not a vehicle green phase."
        )

        print(
            "Pedestrian priority cancelled."
        )

        return

    # ========================================================
    # STEP 1 — YELLOW
    # ========================================================

    print(
        "\nSTEP 1: Yellow transition"
    )

    traci.trafficlight.setPhase(
        TLS_ID,
        yellow_phase
    )

    run_steps(
        YELLOW_TIME
    )

    # ========================================================
    # STEP 2 — ALL RED
    # ========================================================

    print(
        "STEP 2: All-red safety interval"
    )

    current_state = (
        traci.trafficlight.getRedYellowGreenState(
            TLS_ID
        )
    )

    all_red_state = (
        "r" * len(current_state)
    )

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        all_red_state
    )

    print(
        "All-red state        :",
        all_red_state
    )

    run_steps(
        ALL_RED_TIME
    )

    # ========================================================
    # STEP 3 — PEDESTRIAN GREEN
    # ========================================================

    pedestrian_state = (
        create_pedestrian_state(
            active_directions
        )
    )

    print(
        "STEP 3: Pedestrian green"
    )

    print(
        "Pedestrian state     :",
        pedestrian_state
    )

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        pedestrian_state
    )

    print(
        f"Pedestrians crossing "
        f"for {PEDESTRIAN_GREEN_TIME} seconds..."
    )

    run_steps(
        PEDESTRIAN_GREEN_TIME
    )

    # ========================================================
    # STEP 4 — ALL RED CLEARANCE
    # ========================================================

    print(
        "STEP 4: Pedestrian all-red clearance"
    )

    traci.trafficlight.setRedYellowGreenState(
        TLS_ID,
        all_red_state
    )

    run_steps(
        ALL_RED_TIME
    )

    # ========================================================
    # STEP 5 — RESTORE NORMAL PROGRAM
    # ========================================================

    print(
        "STEP 5: Restoring normal traffic signal program"
    )

    # IMPORTANT:
    # Restore the original SUMO program first.

    traci.trafficlight.setProgram(
        TLS_ID,
        "0"
    )

    # Then restore the vehicle green phase.

    traci.trafficlight.setPhase(
        TLS_ID,
        restore_phase
    )

    print(
        f"Vehicle phase restored: {restore_phase}"
    )

    print(
        "Normal traffic signal program restored."
    )

    print(
        "################################################"
    )

    print(
        "Pedestrian priority completed."
    )

    print(
        "################################################\n"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    sumo_cmd = [
        "sumo",
        "-c",
        "pedestrian_test.sumocfg"
    ]

    print(
        "Starting pedestrian priority controller..."
    )

    print(
        f"Simulation target: {SIMULATION_END} seconds"
    )

    # --------------------------------------------------------
    # START SUMO
    # --------------------------------------------------------

    traci.start(
        sumo_cmd
    )

    cooldown = 0

    try:

        # ====================================================
        # MAIN SIMULATION LOOP
        # ====================================================

        while (
            traci.simulation.getTime()
            < SIMULATION_END
        ):

            traci.simulationStep()

            current_time = (
                traci.simulation.getTime()
            )

            # ------------------------------------------------
            # COOLDOWN
            # ------------------------------------------------

            if cooldown > 0:
                cooldown -= 1

            # ------------------------------------------------
            # CHECK EVERY 5 SECONDS
            # ------------------------------------------------

            if int(current_time) % 5 != 0:
                continue

            # ------------------------------------------------
            # GET PEDESTRIAN INFORMATION
            # ------------------------------------------------

            waiting, waiting_time = (
                get_pedestrian_data()
            )

            total_waiting = print_status(
                waiting,
                waiting_time
            )

            # ------------------------------------------------
            # CURRENT TRAFFIC SIGNAL PHASE
            # ------------------------------------------------

            current_phase = (
                traci.trafficlight.getPhase(
                    TLS_ID
                )
            )

            print(
                f"Simulation time : "
                f"{current_time:.0f}s"
            )

            print(
                f"Current phase   : "
                f"{current_phase}"
            )

            # ------------------------------------------------
            # ONLY REQUEST PRIORITY DURING VEHICLE GREEN
            #
            # Phase 0 = NORTH/SOUTH GREEN
            # Phase 2 = EAST/WEST GREEN
            # ------------------------------------------------

            vehicle_green = (
                current_phase in (0, 2)
            )

            # ------------------------------------------------
            # CHECK PEDESTRIAN PRIORITY CONDITION
            # ------------------------------------------------

            if (
                total_waiting >= MIN_WAITING
                and vehicle_green
                and cooldown == 0
            ):

                active_directions = (
                    choose_pedestrian_group(
                        waiting
                    )
                )

                if active_directions:

                    give_pedestrian_priority(
                        active_directions
                    )

                    cooldown = COOLDOWN

        # ====================================================
        # SIMULATION COMPLETE
        # ====================================================

        final_time = (
            traci.simulation.getTime()
        )

        print(
            "\n=========================================="
        )

        print(
            "Simulation completed."
        )

        print(
            f"Final simulation time: "
            f"{final_time:.1f}s"
        )

        print(
            "=========================================="
        )

    finally:

        traci.close()

        print(
            "SUMO simulation closed."
        )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    main()