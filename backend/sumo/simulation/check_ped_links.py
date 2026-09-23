import traci

TLS_ID = "center"

def main():

    traci.start([
        "sumo",
        "-c",
        "pedestrian_test.sumocfg"
    ])

    try:

        links = traci.trafficlight.getControlledLinks(TLS_ID)

        print("\n========== ALL TRAFFIC LIGHT LINKS ==========\n")

        for index, connection_group in enumerate(links):

            print(f"LINK INDEX {index}")

            for connection in connection_group:

                print(
                    "   ",
                    connection
                )

        print("\n=============================================")

    finally:

        traci.close()


if __name__ == "__main__":
    main()