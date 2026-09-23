import traci

SUMO_BINARY = "sumo"

traci.start([
    SUMO_BINARY,
    "-c",
    "traffic.sumocfg"
])

for step in range(300):

    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()

    if step % 20 == 0:

        print("\n==============================")
        print("Simulation Time:", step)
        print("Vehicles:", len(vehicles))

        for veh_id in vehicles[:10]:

            route = traci.vehicle.getRoute(veh_id)
            index = traci.vehicle.getRouteIndex(veh_id)

            print(
                veh_id,
                "Route:",
                route,
                "Current Edge:",
                traci.vehicle.getRoadID(veh_id)
            )

traci.close()

print("\nSimulation finished.")