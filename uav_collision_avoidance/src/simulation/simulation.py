"""Simulation module"""

import csv
import logging
import datetime
from typing import List
from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent, QVector3D
from PySide6.QtWidgets import QMainWindow, QApplication

from src.aircraft.aircraft import Aircraft
from src.aircraft.aircraft_fcc import AircraftFCC
from src.simulation.simulation_settings import SimulationSettings
from src.simulation.simulation_physics import SimulationPhysics
from src.simulation.simulation_state import SimulationState
from src.simulation.simulation_render import SimulationRender
from src.simulation.simulation_widget import SimulationWidget
from src.simulation.simulation_adsb import SimulationADSB
from src.simulation.simulation_fps import SimulationFPS

class Simulation(QMainWindow):
    """Main simulation App"""

    def __init__(self, aircrafts : List[Aircraft] | None = None, simulation_time : int = 100_000) -> None:
        super().__init__()
        SimulationSettings().__init__()
        if aircrafts is None:
            self.aircrafts : List[Aircraft] = [
                Aircraft(
                    position = QVector3D(100, 1000, 1000),
                    speed = QVector3D(60, -70, 0),
                    initial_target = QVector3D(1000_000, -1000_000, 1000)),
                Aircraft(
                    position = QVector3D(900, 1300, 1000),
                    speed = QVector3D(0, -70, 0),
                    initial_target = QVector3D(0, -1000_000, 1000)),
            ]
        else:
            self.aircrafts = aircrafts
        self.simulation_time : int = simulation_time
        self.state : SimulationState | None = None

    def run_realtime(self) -> None:
        """Executes realtime simulation"""
        if self.state is not None:
            print("Another instance already running")
            return
        logging.info("Starting realtime simulation")
        self.state = SimulationState(SimulationSettings(), is_realtime = True)

        self.simulation_physics = SimulationPhysics(self, self.aircrafts, self.state)
        self.simulation_physics.start(priority = QThread.Priority.TimeCriticalPriority)

        self.simulation_adsb = SimulationADSB(self, self.aircrafts, self.state)
        self.simulation_adsb.start(priority = QThread.Priority.NormalPriority)

        self.simulation_fps = SimulationFPS(self, self.state)
        self.simulation_fps.start(priority = QThread.Priority.NormalPriority)

        self.simulation_widget = SimulationWidget(self.aircrafts, self.simulation_fps, self.state)
        self.simulation_widget.show()

        self.simulation_render = SimulationRender(self, self.simulation_widget, self.state)
        self.simulation_render.start(priority = QThread.Priority.NormalPriority)

        self.simulation_widget.stop_signal.connect(self.stop_simulation)
        return
    
    def run_prerender(self) -> None:
        """Executes prerender simulation"""
        if self.state is not None:
            print("Another instance already running")
            return
        logging.info("Starting prerendered simulation")
        self.state = SimulationState(SimulationSettings(), is_realtime = False)
        simulation_physics = SimulationPhysics(self, self.aircrafts, self.state)
        simulation_adsb = SimulationADSB(self, self.aircrafts, self.state)
        time_step : int = int(self.state.simulation_threshold)
        adsb_step : int = int(self.state.adsb_threshold)
        partial_time_counter : int = adsb_step
        for time in range(0, self.simulation_time, time_step):
            print(time)
            simulation_physics.cycle(time_step)
            if partial_time_counter >= adsb_step:
                simulation_adsb.cycle()
                partial_time_counter = 0
            partial_time_counter += time_step
            if self.state.collision:
                break
        self.stop_simulation()
        return
    
    def stop_simulation(self) -> None:
        """Stops simulation"""
        if self.state.is_realtime:
            self.stop_realtime_simulation()
        else:
            self.stop_prerender_simulation()
        self.state.reset()
        self.state.is_running = False
        return

    def stop_realtime_simulation(self) -> None:
        """Finishes all active realtime simulation threads"""
        if not self.state.is_running:
            return
        logging.info("Stopping realtime simulation")

        self.simulation_physics.requestInterruption()
        self.simulation_adsb.requestInterruption()
        self.simulation_render.requestInterruption()
        self.simulation_fps.requestInterruption()

        self.simulation_physics.quit()
        self.simulation_physics.wait()

        if self.state.is_paused:
            self.state.append_paused_time()
        simulated_time : float = self.state.physics_cycles / (1000 / self.state.simulation_threshold)
        real_time_pauses : float = self.simulation_physics.global_start_timestamp.msecsTo(self.simulation_physics.global_stop_timestamp) / 1000
        real_time : float = real_time_pauses - (self.state.time_paused / 1000)
        print("Time simulated: " + "{:.2f}".format(simulated_time) + "s")
        if real_time == real_time_pauses:
            print("Time elapsed: " + "{:.2f}".format(real_time) + "s")
        else:
            print("Time elapsed: " + "{:.2f}".format(real_time) + "s (" + "{:.2f}".format(real_time_pauses) + "s with pauses)")
        if real_time != 0:
            print("Time efficiency: " + "{:.2f}".format(simulated_time / real_time * 100) + "%")
            logging.info("Calculated time efficiency: " + "{:.2f}".format(simulated_time / real_time * 100) + "%")

        self.export_visited_locations()

        self.simulation_adsb.quit()
        self.simulation_adsb.wait()
        self.simulation_render.quit()
        self.simulation_render.wait()
        self.simulation_fps.quit()
        self.simulation_fps.wait()
        return
    
    def stop_prerender_simulation(self) -> None:
        """Finishes all active prerender simulation threads"""
        if not self.state.is_running:
            return
        logging.info("Stopping prerender simulation")
        # todo
        return
    
    def export_visited_locations(self) -> None:
        """Exports aircrafts visited location lists"""
        export_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        aircraft_fccs : List[AircraftFCC] = [aircraft.fcc for aircraft in self.aircrafts]
        for aircraft in aircraft_fccs:
            try:
                Path("logs/visited").mkdir(parents=True, exist_ok=True)
            except:
                return
            file = open(f"logs/visited/visited-aircraft-{aircraft.aircraft_id}-{export_time}.csv", "w")
            writer = csv.writer(file)
            writer.writerow(["x","y","z"])
            for position in aircraft.visited:
                writer.writerow([("{:.2f}".format(position.x())),("{:.2f}".format(position.y())),("{:.2f}".format(position.z()))])
        return
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Qt method performed on the main window close event"""
        self.stop_simulation()
        event.accept()
        return super().closeEvent(event)
