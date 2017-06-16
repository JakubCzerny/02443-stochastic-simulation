import time

from vehicle import Vehicle
from simulation import Simulation
from visualisation import Visualisation 

def start_sim():
    time_delta = 0.1 # << seconds, vv meters
    sim = Simulation(nb_lanes=3, road_len=100)
    vis = Visualisation(sim)

    try:
        while True:
            sim.time_step(time_delta)   # update simulation step
            if vis.update():            # update visualisation step
                break                   # break the outer loop if needed
            time.sleep(time_delta)      # sleep for some time
    except KeyboardInterrupt:
        print()
        print("Simulation interrupted.")

if __name__ == "__main__":
    start_sim()

