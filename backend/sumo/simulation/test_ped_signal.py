import traci


def main():

    traci.start([
        "sumo",
        "-c",
        "pedestrian_test.sumocfg"
    ])

    try:

        links = {
            "NORTH": 20,
            "EAST": 21,
            "SOUTH": 22,
            "WEST": 23
        }

        print("\n========== PEDESTRIAN SIGNAL TEST ==========")

        for direction, index in links.items():

            state = ["r"] * 24
            state[index] = "G"

            state = "".join(state)

            print(f"{direction}:")
            print(f"  Index : {index}")
            print(f"  State : {state}")
            print()

        print("============================================")

    finally:

        traci.close()


if __name__ == "__main__":
    main()