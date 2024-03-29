"""Simulation ADS-B system simulation thread module"""

import logging
from typing import List

from PySide6.QtCore import QThread, QTime
from PySide6.QtGui import QVector3D
from PySide6.QtWidgets import QMainWindow

from src.aircraft.aircraft import Aircraft
from src.aircraft.aircraft_vehicle import AircraftVehicle
from src.aircraft.aircraft_fcc import AircraftFCC
from src.simulation.simulation_state import SimulationState

class SimulationADSB(QThread):
    """Thread running ADS-B system for collision detection and avoidance"""

    def __init__(self, parent : QMainWindow, aircrafts : List[Aircraft], simulation_state : SimulationState) -> None:
        super(SimulationADSB, self).__init__(parent)
        self.aircrafts = aircrafts
        self.aircraft_vehicles : List[AircraftVehicle] = [aircraft.vehicle for aircraft in self.aircrafts]
        self.aircraft_fccs : List[AircraftFCC] = [aircraft.fcc for aircraft in self.aircrafts]
        self.simulation_state = simulation_state
        self.adsb_cycles : int = 0
        
    def run(self) -> None:
        """Runs ADS-B simulation thread with precise timeout"""
        while not self.isInterruptionRequested():
            start_timestamp = QTime.currentTime()
            self.cycle()
            self.msleep(max(0, self.simulation_state.adsb_threshold - start_timestamp.msecsTo(QTime.currentTime())))
        return super().run()
    
    def cycle(self) -> None:
        """Executes ADS-B simulation cycle"""
        aircraft_vehicle_1 : AircraftVehicle = self.aircraft_vehicles[0]
        aircraft_vehicle_2 : AircraftVehicle = self.aircraft_vehicles[1]

        if not self.simulation_state.is_paused:
            self.adsb_cycles += 1
            self.simulation_state.update_adsb_settings()

            relative_position = aircraft_vehicle_1.position - aircraft_vehicle_2.position
            speed_difference = aircraft_vehicle_1.speed - aircraft_vehicle_2.speed
            time_to_closest_approach = -(QVector3D.dotProduct(relative_position, speed_difference) / QVector3D.dotProduct(speed_difference, speed_difference))
            print("Time to closest approach: " + "{:.2f}".format(time_to_closest_approach) + "s")

            if time_to_closest_approach > 0:
                # miss distance at closest approach
                speed_difference_unit = speed_difference.normalized()
                miss_distance_vector : QVector3D = QVector3D.crossProduct(
                    speed_difference_unit,
                    QVector3D.crossProduct(relative_position, speed_difference_unit))
                print("Miss distance at closest approach: " + "{:.2f}".format(miss_distance_vector.length()) + "m")

                if miss_distance_vector.length() == 0:
                    print("Head-on collision detected")

                # resolve confict condition
                minimum_separation = 100
                unresolved_region = minimum_separation - miss_distance_vector.length()
                if unresolved_region > 0:
                    print("Conflict condition detected")
                    if not self.aircraft_fccs[0].evade_maneuver:
                        self.aircraft_fccs[0].apply_evade_maneuver()
                
                # probable collision
                collision_distance = aircraft_vehicle_1.size / 2 + aircraft_vehicle_2.size / 2
                collision_region = collision_distance - miss_distance_vector.length()
                if collision_region > 0:
                    print("Probable collision detected")

            for aircraft in self.aircraft_vehicles:
                # path
                self.aircraft_fccs[aircraft.aircraft_id].append_visited()

                # console output
                if self.simulation_state.adsb_report and aircraft.aircraft_id == 0:
                    self.print_adsb_report(aircraft)

    def print_adsb_report(self, aircraft : AircraftVehicle) -> None:
        """Prints ADS-B report for the aircraft to the console"""
        print("Aircraft id: " + str(aircraft.aircraft_id) +
            "; speed: " + "{:.2f}".format(aircraft.absolute_speed) +
            "; target speed: " + "{:.2f}".format(self.aircraft_fccs[aircraft.aircraft_id].target_speed) +
            "; x: " + "{:.2f}".format(aircraft.position.x()) +
            "; y: " + "{:.2f}".format(aircraft.position.y()) +
            "; yaw angle: " + "{:.2f}".format(aircraft.yaw_angle) +
            "; target yaw angle: " + "{:.2f}".format(self.aircraft_fccs[aircraft.aircraft_id].target_yaw_angle) +
            "; pitch angle: " + "{:.2f}".format(aircraft.pitch_angle) +
            "; roll angle: " + "{:.2f}".format(aircraft.roll_angle) +
            "; target roll angle: " + "{:.2f}".format(self.aircraft_fccs[aircraft.aircraft_id].target_roll_angle) +
            "; distance covered: " + "{:.2f}".format(aircraft.distance_covered) +
            "; fps: " + "{:.2f}".format(self.simulation_state.fps) +
            "; t: " + str(self.adsb_cycles) +
            "; phys: " + str(self.simulation_state.physics_cycles))
