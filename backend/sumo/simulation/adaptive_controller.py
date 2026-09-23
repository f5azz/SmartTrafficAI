import traci


# ============================================
# SMART TRAFFIC AI
# SAFE ADAPTIVE TRAFFIC CONTROLLER
# ============================================

SUMO_BINARY = "sumo"

TLS_ID = "center"

APPROACHES = {
    "NORTH": "north_to_center",
    "SOUTH": "south_to_center",
    "EAST": "east_to_center",
    "WEST": "west_to_center"
}


# ============================================
# Congestion
# ============================================

def get_congestion(vehicle_count):

    if vehicle_count <= 5:
        return "LOW"

    elif vehicle_count <= 10:
        return "MEDIUM"

    else:
        return "HIGH"


# ============================================
# Green time
# ============================================

def calculate_green_time(demand):

    MIN_GREEN = 20
    MAX_GREEN = 60

    green_time = MIN_GREEN + (demand * 2)

    return min(MAX_GREEN, max(MIN_GREEN, green_time))


# ============================================
# Traffic data
# ============================================

def get_traffic_data():

    traffic = {}

    for direction, edge in APPROACHES.items():

        vehicles = traci.edge.getLastStepVehicleNumber(edge)

        queue = traci.edge.getLastStepHaltingNumber(edge)

        waiting = traci.edge.getWaitingTime(edge)

        congestion = get_congestion(vehicles)

        traffic[direction] = {
            "vehicles": vehicles,
            "queue": queue,
            "waiting": waiting,
            "congestion": congestion
        }

    return traffic


# ============================================
# AI traffic score
# ============================================

def calculate_priority(traffic):

    scores = {}

    for direction, data in traffic.items():

        score = (
            data["vehicles"]
            + data["queue"] * 2
            + data["waiting"] * 0.1
        )

        scores[direction] = score

    priority = max(scores, key=scores.get)

    return priority, scores


# ============================================
# Determine required signal group
# ============================================

def get_required_group(priority):

    if priority in ["NORTH", "SOUTH"]:
        return "NS"

    return "EW"


# ============================================
# Start SUMO
# ============================================

traci.start([
    SUMO_BINARY,
    "-c",
    "traffic.sumocfg"
])


try:

    current_group = "NS"

    next_decision = 0

    green_time = 30

    for step in range(600):

        traci.simulationStep()


        # ====================================
        # AI DECISION
        # ====================================

        if step >= next_decision:

            traffic = get_traffic_data()

            priority, scores = calculate_priority(traffic)

            required_group = get_required_group(priority)

            demand = traffic[priority]["vehicles"]

            new_green_time = calculate_green_time(demand)


            # ==================================
            # SAME SIGNAL GROUP
            # ==================================

            if required_group == current_group:

                if current_group == "NS":

                    traci.trafficlight.setPhase(
                        TLS_ID,
                        0
                    )

                else:

                    traci.trafficlight.setPhase(
                        TLS_ID,
                        2
                    )

                traci.trafficlight.setPhaseDuration(
                    TLS_ID,
                    new_green_time
                )

                green_time = new_green_time

                next_decision = step + 20


            # ==================================
            # SWITCH NS → EW
            # ==================================

            elif current_group == "NS" and required_group == "EW":

                print("\nAI REQUESTS: NORTH/SOUTH → EAST/WEST")

                # Yellow phase
                traci.trafficlight.setPhase(
                    TLS_ID,
                    1
                )

                traci.trafficlight.setPhaseDuration(
                    TLS_ID,
                    3
                )

                current_group = "EW"

                green_time = new_green_time

                next_decision = step + 3


            # ==================================
            # SWITCH EW → NS
            # ==================================

            elif current_group == "EW" and required_group == "NS":

                print("\nAI REQUESTS: EAST/WEST → NORTH/SOUTH")

                # Yellow phase
                traci.trafficlight.setPhase(
                    TLS_ID,
                    3
                )

                traci.trafficlight.setPhaseDuration(
                    TLS_ID,
                    3
                )

                current_group = "NS"

                green_time = new_green_time

                next_decision = step + 3


            # ==================================
            # DISPLAY
            # ==================================

            print("\n")
            print("========================================")
            print("          SMART TRAFFIC AI")
            print("========================================")

            print(
                f"Simulation Time : {step} sec"
            )

            print("----------------------------------------")

            print(
                f"NORTH : {traffic['NORTH']['vehicles']:2d} "
                f"vehicles | Queue: {traffic['NORTH']['queue']:2d} "
                f"| Wait: {traffic['NORTH']['waiting']:.1f}s "
                f"| {traffic['NORTH']['congestion']}"
            )

            print(
                f"SOUTH : {traffic['SOUTH']['vehicles']:2d} "
                f"vehicles | Queue: {traffic['SOUTH']['queue']:2d} "
                f"| Wait: {traffic['SOUTH']['waiting']:.1f}s "
                f"| {traffic['SOUTH']['congestion']}"
            )

            print(
                f"EAST  : {traffic['EAST']['vehicles']:2d} "
                f"vehicles | Queue: {traffic['EAST']['queue']:2d} "
                f"| Wait: {traffic['EAST']['waiting']:.1f}s "
                f"| {traffic['EAST']['congestion']}"
            )

            print(
                f"WEST  : {traffic['WEST']['vehicles']:2d} "
                f"vehicles | Queue: {traffic['WEST']['queue']:2d} "
                f"| Wait: {traffic['WEST']['waiting']:.1f}s "
                f"| {traffic['WEST']['congestion']}"
            )

            print("----------------------------------------")

            print(
                "AI PRIORITY :",
                priority
            )

            print(
                "ACTIVE GROUP :",
                "NORTH/SOUTH"
                if current_group == "NS"
                else "EAST/WEST"
            )

            print(
                "GREEN TIME :",
                green_time,
                "seconds"
            )

            print("----------------------------------------")

            print(
                "AI SCORES :",
                {
                    k: round(v, 1)
                    for k, v in scores.items()
                }
            )

            print("========================================")


finally:

    traci.close()

    print("\nSimulation finished.")