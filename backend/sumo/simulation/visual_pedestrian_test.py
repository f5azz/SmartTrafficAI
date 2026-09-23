import traci

TLS_ID = "center"

SIMULATION_END = 600

PEDESTRIAN_LINKS = {
    "NORTH": 20,
    "EAST": 21,
    "SOUTH": 22,
    "WEST": 23
}


def run_steps(seconds):

    for _ in range(seconds):

        if traci.simulation.getTime() >= SIMULATION_END:
            return

        traci.simulationStep()


def pedestrian_green(directions):

    current_state = traci.trafficlight.getRedYellowGreenState(TLS_ID)

    state = ["r"] * len(current_state)

    for direction in directions:

        index = PEDESTRIAN_LINKS[direction]

        state[index] = "G"

    return "".join(state)


def main():

    print("Starting visual pedestrian test...")

    # IMPORTANT:
    # Use SUMO-GUI instead of SUMO
    sumo_cmd = [
        "sumo-gui",
        "-c",
        "pedestrian_test.sumocfg"
    ]

    traci.start(sumo_cmd)

    try:

        print("SUMO-GUI started.")
        print("Watch the intersection visually.")

        # Let normal traffic run
        run_steps(20)

        print("\nTesting NORTH + SOUTH pedestrian crossing")

        # All vehicle signals red
        current_state = traci.trafficlight.getRedYellowGreenState(TLS_ID)

        all_red = "r" * len(current_state)

        traci.trafficlight.setRedYellowGreenState(
            TLS_ID,
            all_red
        )

        run_steps(2)

        # Give NORTH + SOUTH pedestrians green
        state = pedestrian_green([
            "NORTH",
            "SOUTH"
        ])

        print("Pedestrian signal:")
        print(state)

        traci.trafficlight.setRedYellowGreenState(
            TLS_ID,
            state
        )

        print("Pedestrian GREEN for 15 seconds...")

        run_steps(15)

        # All red again
        traci.trafficlight.setRedYellowGreenState(
            TLS_ID,
            all_red
        )

        run_steps(2)

        print("\nTesting EAST + WEST pedestrian crossing")

        state = pedestrian_green([
            "EAST",
            "WEST"
        ])

        print("Pedestrian signal:")
        print(state)

        traci.trafficlight.setRedYellowGreenState(
            TLS_ID,
            state
        )

        print("Pedestrian GREEN for 15 seconds...")

        run_steps(15)

        print("\nVisual pedestrian test completed.")

        # Continue normal simulation
        traci.trafficlight.setProgram(TLS_ID, "0")

        run_steps(20)

    finally:

        traci.close()

        print("SUMO-GUI closed.")


if __name__ == "__main__":
    main()