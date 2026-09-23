import traci


# SUMO pedestrian crossing IDs
CROSSINGS = {
    "NORTH": ":center_c0",
    "EAST": ":center_c1",
    "SOUTH": ":center_c2",
    "WEST": ":center_c3"
}


def get_pedestrian_data():

    data = {}

    for direction in CROSSINGS:

        data[direction] = {
            "waiting": 0,
            "crossing": 0,
            "waiting_time": 0.0
        }

    pedestrian_ids = traci.person.getIDList()

    for person_id in pedestrian_ids:

        current_edge = traci.person.getRoadID(person_id)

        next_edge = traci.person.getNextEdge(person_id)

        waiting_time = traci.person.getWaitingTime(person_id)

        # -----------------------------------------
        # PERSON IS CURRENTLY ON A ZEBRA CROSSING
        # -----------------------------------------

        for direction, crossing_id in CROSSINGS.items():

            if current_edge == crossing_id:

                data[direction]["crossing"] += 1

        # -----------------------------------------
        # PERSON IS WAITING TO ENTER A CROSSING
        # -----------------------------------------

        for direction, crossing_id in CROSSINGS.items():

            if next_edge == crossing_id and waiting_time > 0:

                data[direction]["waiting"] += 1

                data[direction]["waiting_time"] += waiting_time

    return data


def get_demand(waiting):

    if waiting >= 5:
        return "HIGH"

    elif waiting >= 2:
        return "MEDIUM"

    elif waiting == 1:
        return "LOW"

    return "NONE"


def print_pedestrian_data(data):

    print("\n========== PEDESTRIAN ANALYSIS ==========")

    total_waiting = 0
    total_crossing = 0

    for direction, values in data.items():

        waiting = values["waiting"]
        crossing = values["crossing"]
        waiting_time = values["waiting_time"]

        demand = get_demand(waiting)

        total_waiting += waiting
        total_crossing += crossing

        print(
            f"{direction:<6} | "
            f"Waiting: {waiting:<3} | "
            f"Crossing: {crossing:<3} | "
            f"Wait Time: {waiting_time:>6.1f}s | "
            f"Demand: {demand}"
        )

    print("------------------------------------------")

    print(f"TOTAL WAITING   : {total_waiting}")
    print(f"TOTAL CROSSING  : {total_crossing}")

    print("==========================================")


def main():

    sumo_cmd = [
        "sumo",
        "-c",
        "pedestrian_test.sumocfg"
    ]

    print("Starting pedestrian monitoring...")

    traci.start(sumo_cmd)

    try:

        for step in range(600):

            traci.simulationStep()

            if step % 20 == 0:

                data = get_pedestrian_data()

                print(f"\nSimulation Time: {step}s")

                print_pedestrian_data(data)

    finally:

        traci.close()

        print("\nSUMO simulation closed.")


if __name__ == "__main__":

    main()