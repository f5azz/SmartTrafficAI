import traci

from sumo_service import start_sumo
from traffic_controller import make_adaptive_decision


print("Starting SUMO...")

start_sumo()

print("Running 4-phase clockwise adaptive controller...")


for step in range(180):

    if not traci.isLoaded():
        break

    traci.simulationStep()

    decision = make_adaptive_decision()

    print()
    print("=" * 55)
    print(
        "Simulation Time:",
        traci.simulation.getTime()
    )
    print(
        "Priority:",
        decision["priority_direction"]
    )
    print(
        "Current Signal:",
        decision["current_group"]
    )
    print(
        "Green Time:",
        decision["green_time"]
    )
    print(
        "Emergency:",
        decision["emergency"]
    )
    print(
        "Signal Switched:",
        decision["signal_switched"]
    )
    print("=" * 55)


if traci.isLoaded():
    traci.close()

print()
print("4-phase controller test completed.")