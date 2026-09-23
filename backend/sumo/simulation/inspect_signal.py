import traci
import os

sumo_config = os.path.join(
    os.path.dirname(__file__),
    "traffic.sumocfg"
)

traci.start([
    "sumo",
    "-c",
    sumo_config
])

print("\n==============================")
print("TRAFFIC LIGHT INFORMATION")
print("==============================")

tls_ids = traci.trafficlight.getIDList()

print("Traffic light IDs:")
print(tls_ids)

for tls_id in tls_ids:

    print("\n------------------------------")
    print("Traffic Light:", tls_id)

    logic_list = traci.trafficlight.getAllProgramLogics(tls_id)

    for logic in logic_list:

        print("Program ID:", logic.programID)
        print("Current phase:", traci.trafficlight.getPhase(tls_id))

        print("\nPhases:")

        for i, phase in enumerate(logic.phases):

            print(
                f"Phase {i}: "
                f"duration={phase.duration}s "
                f"state={phase.state}"
            )

print("\n==============================")
print("Finished inspection")
print("==============================")

traci.close()