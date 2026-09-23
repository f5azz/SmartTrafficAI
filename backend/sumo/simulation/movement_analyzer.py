import traci

# Approach edges
APPROACHES = {
    "NORTH": "north_to_center",
    "SOUTH": "south_to_center",
    "EAST": "east_to_center",
    "WEST": "west_to_center"
}

# Movement mapping
# We use destination direction instead of left/right for now.
MOVEMENTS = {
    "NORTH": {
        "STRAIGHT": "center_to_south",
        "TURN_TO_EAST": "center_to_east",
        "TURN_TO_WEST": "center_to_west"
    },

    "SOUTH": {
        "STRAIGHT": "center_to_north",
        "TURN_TO_EAST": "center_to_east",
        "TURN_TO_WEST": "center_to_west"
    },

    "EAST": {
        "STRAIGHT": "center_to_west",
        "TURN_TO_NORTH": "center_to_north",
        "TURN_TO_SOUTH": "center_to_south"
    },

    "WEST": {
        "STRAIGHT": "center_to_east",
        "TURN_TO_NORTH": "center_to_north",
        "TURN_TO_SOUTH": "center_to_south"
    }
}


def get_movement_data():

    movement_data = {}

    for direction in APPROACHES:

        movement_data[direction] = {}

        for movement in MOVEMENTS[direction]:
            movement_data[direction][movement] = 0

    # Get all vehicles currently in simulation
    vehicle_ids = traci.vehicle.getIDList()

    for vehicle_id in vehicle_ids:

        current_edge = traci.vehicle.getRoadID(vehicle_id)

        # Ignore vehicles inside intersection
        if current_edge.startswith(":"):
            continue

        # Check which approach the vehicle belongs to
        for direction, approach_edge in APPROACHES.items():

            if current_edge != approach_edge:
                continue

            # Get vehicle route
            route = traci.vehicle.getRoute(vehicle_id)

            if len(route) < 2:
                continue

            # The second edge tells us where the vehicle is going
            destination_edge = route[1]

            # Identify movement
            for movement, target_edge in MOVEMENTS[direction].items():

                if destination_edge == target_edge:

                    movement_data[direction][movement] += 1

                    break

    return movement_data


def print_movement_data(data):

    print("\n========== MOVEMENT ANALYSIS ==========")

    for direction in data:

        print(f"\n{direction}")

        for movement, count in data[direction].items():

            print(f"  {movement:<15}: {count}")

    print("========================================")


def main():

    sumo_binary = "sumo"

    sumo_cmd = [
        sumo_binary,
        "-c",
        "../simulation/traffic.sumocfg"
    ]

    print("Starting SUMO...")

    traci.start(sumo_cmd)

    try:

        for step in range(600):

            traci.simulationStep()

            # Analyze every 20 seconds
            if step % 20 == 0:

                data = get_movement_data()

                print(f"\nSimulation Time: {step}s")

                print_movement_data(data)

    finally:

        traci.close()

        print("\nSUMO simulation closed.")


if __name__ == "__main__":
    main()