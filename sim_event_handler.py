import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class SimEventHandler:
    """
    A simulation handler allows you to add additional behavior to the base
    simulation, e.g. to collect statistics or modify car behavior.

    It contains a bunch of methods that are called by the simulation at
    specific moments in the simulation. These methods should be overwritten by
    sub-classes.
    """

    enabled = True

    def before_time_step(self, dt, sim_time):
        pass

    def after_time_step(self, dt, sim_time):
        pass

    def before_vehicle_update(self, dt, vehicle):
        pass

    def after_vehicle_update(self, dt, vehicle):
        pass

    def after_vehicle_spawn(self, vehicle, sim_time):
        pass

    def before_vehicle_despawn(self, vehicle, sim_time):
        pass

    def __str__(self):
        return self.__class__.__name__

class SlowZoneEvHandler(SimEventHandler):
    """
    Simulation handler that forces cars to go slow down in a certain section of
    the road.
    """

    def __init__(self, start, stop, max_velocity=10):
        """ Section of road defined by [start, stop], in meters. """
        self._start = start
        self._stop = stop
        self._max_velocity = max_velocity
        self._acc = -3
        self.simTimeList = []
        self.enableList = []

    def after_vehicle_update(self, dt, vehicle):
        if self.enabled and vehicle.position > self._start and vehicle.position < self._stop:
            if vehicle.velocity > self._max_velocity and vehicle.acceleration > self._acc:
                vehicle.acceleration = self._acc

    def after_time_step(self, dt, sim_time):
        self.simTimeList.append(sim_time)
        if self.enabled:
            self.enableList.append(1)

        else:
            self.enableList.append(0)

    def plot(self, subplot = False):
        plt.plot(self.simTimeList, self.enableList)
        plt.grid()
        plt.ylabel("On/off [1/0]",  fontsize = 20)
        plt.title("On/Off status of slow zone from {}m to {}m with max_velocity {:.2f}".format(self._start, self._stop, self._max_velocity),  fontsize = 20)
        if not subplot:
            plt.xlabel("Time [s]")
    def __str__(self):
        return "{}: max_velocity={}".format(self.__class__.__name__, self._max_velocity)

class StatsEvHandler(SimEventHandler):
    """
    Simulation handler that collects statistics.
    """

    def __init__(self):
        self.unspawned_count = 0

    def before_vehicle_despawn(self, vehicle, sim_time):
        self.unspawned_count += 1

    def __str__(self):
        return """
        Statistics summary:
         - unspawned_count: {}
        """.format(self.unspawned_count)

class AverageSpeedHandler(SimEventHandler):

    """
    Tracks the average speed of the vehicles.
    """
    def __init__(self):
        self.averageSpeed = 0
        self.numberOfVehicles = 0
        self.averageSpeedList = []
        self.simTimeList = []
        self.updatecount = 0

    def after_vehicle_update(self, dt, vehicle):
        self.averageSpeed += vehicle.velocity
        self.numberOfVehicles += 1

    def after_time_step(self, dt, sim_time):
        self.updatecount += 1
        if self.updatecount > 1: #Only update ever 3. timestep
            if self.numberOfVehicles > 0:
                self.averageSpeedList.append(self.averageSpeed / self.numberOfVehicles)
                self.averageSpeed = 0
                self.numberOfVehicles = 0
                self.simTimeList.append(sim_time)
            self.updatecount = 0

    def plot(self, subplot = False):
        windowSize = 5
        speed = pd.DataFrame(self.averageSpeedList)
        r = speed.rolling(window = windowSize) # Average last 10 values
        r = r.mean()
        

        if not subplot:
            plt.figure()

        #plt.plot(self.simTimeList,speed, linewidth = 2)
        plt.plot(self.simTimeList[3:],r[3:], linewidth = 3)
        plt.grid()

        plt.ylabel("Average speed of cars [m/s]", fontsize = 20)
        #plt.title("Average speed of cars as function of time, rolling window = {}".format(windowSize), fontsize = 20)
        #plt.rcParams.update({'font.size': 45})
        if not subplot:
            plt.show()
            plt.xlabel("Time [s]", fontsize = 23)
        #print(len(self.simTimeList))

class ThroughPutHandler(SimEventHandler):

    def __init__(self):
        self.nb_vehicles = 0
        self.nb_vehicles_list = []
        self.interval = 15 # seconds
        self.max_time = 0

    def before_vehicle_despawn(self, vehicle, sim_time):
        self.nb_vehicles += 1

    def after_time_step(self, dt, sim_time):
        if len(self.nb_vehicles_list) < sim_time // self.interval:
            self.nb_vehicles_list.append(self.nb_vehicles)
            self.nb_vehicles = 0
            self.max_time = sim_time

    def plot(self, subplot = False):
        if len(self.nb_vehicles_list) == 0:
            return

        print("Average/min/max throughput",
                np.mean(self.nb_vehicles_list),
                np.min(self.nb_vehicles_list),
                np.max(self.nb_vehicles_list))

        if not subplot:
            plt.figure()
            plt.xlabel("Time [s]", fontsize = 23)

        plt.ylabel("Throughput [vehicles/{}s]".format(self.interval), fontsize = 20)
        plt.plot(np.linspace(0, self.max_time, len(self.nb_vehicles_list)), self.nb_vehicles_list, '-b*',linewidth = 3)
        plt.grid()
        if not subplot:
            plt.show()

class TravelTimeHandler(SimEventHandler):

    def __init__(self):
        self.dict = {}

    def after_vehicle_spawn(self, vehicle, sim_time):
        self.dict[vehicle] = (sim_time, 0)

    def before_vehicle_despawn(self, vehicle, sim_time):
        p = self.dict[vehicle]
        self.dict[vehicle] = (p[0], sim_time - p[0])

    def plot(self, subplot = False):
        times = []
        travel_times = []

        for k in self.dict:
            p = self.dict[k]
            if p[1] != 0:
                times.append(p[0])
                travel_times.append(p[1])

        if len(times) == 0:
            return

        print("Average/min/max travel times",
                np.mean(travel_times),
                np.min(travel_times),
                np.max(travel_times))

        if not subplot:
            plt.figure()


        windowSize = 8
        times = np.array(times)
        travel_times = np.array(travel_times)
        indicies = np.argsort(times)
        times = times[indicies]
        travel_times = travel_times[indicies]

        travel_times = pd.DataFrame(travel_times)
        r = travel_times.rolling(window = windowSize)
        r = r.mean()
        


        plt.ylabel("Travel time [s]", fontsize = 20)
        plt.plot(times, r, linewidth = 3)
        plt.grid()
        if not subplot:
            plt.xlabel("Time [s]", fontsize = 23)
            plt.show()

class VehicleCountHandler(SimEventHandler):

    def __init__(self):
        self.count = 0
        self.counts = []
        self.max_time = 0

    def before_vehicle_update(self, dt, vehicle):
        self.count += 1

    def after_time_step(self, dt, sim_time):
        self.max_time = sim_time
        self.counts.append(self.count)
        self.count = 0

    def plot(self, subplot = False):
        if len(self.counts) == 0:
            return

        x = np.linspace(0, self.max_time, len(self.counts))

        if not subplot:
            plt.figure()

        plt.plot(x, self.counts, linewidth = 3)
        plt.ylabel("Number of vehicles \n on the road", fontsize = 20)
        plt.grid()
        plt.xlabel("Time [s]", fontsize = 23)
        if not subplot:
            plt.show()
 