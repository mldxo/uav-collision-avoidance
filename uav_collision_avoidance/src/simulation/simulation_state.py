"""Simulation state module"""

from PySide6.QtCore import QSettings, QTime, QMutex, QMutexLocker
from PySide6.QtGui import QPixmap

from src.simulation.simulation_settings import SimulationSettings

class SimulationState(QSettings):
    """Class defining simulation's traits"""

    def __init__(self, simulation_settings : SimulationSettings, is_realtime : bool = True) -> None:
        super(SimulationState, self).__init__()
        self.__mutex : QMutex = QMutex()

        # simulation state
        self.simulation_settings = simulation_settings
        self.update_settings()
        self.is_realtime : bool = is_realtime
        # self.time_scale : float = 1.0 # define slow motion or fast forward
        self.physics_cycles : int = 0
        self.is_paused : bool = False
        self.is_running : bool = True
        self.__reset_demanded : bool = False
        self.pause_start_timestamp : QTime | None = None
        self.time_paused : int = 0 # ms
        self.__adsb_report : bool = False
        self.__collision : bool = False
        self.__first_cause_collision : bool = False
        self.__second_cause_collision : bool = False

        # render state
        self.__gui_scale : float = 0.75 # define gui scaling
        self.fps : float = 0.0
        self.draw_fps : bool = True
        self.draw_aircraft : bool = True
        self.draw_grid : bool = False
        self.draw_path : bool = True
        self.draw_speed_vectors : bool = True
        self.draw_safezones : bool = True
        self.draw_miss_distance_vector : bool = True

        # assets
        self.aircraft_pixmap : QPixmap = QPixmap()
        self.aircraft_pixmap.load("src/assets/aircraft.png")
    
    @property
    def adsb_report(self) -> None:
        """Returns ADS-B commandline info reporting flag"""
        return self.__adsb_report

    def update_settings(self) -> None:
        """Updates all state settings"""
        self.update_render_settings()
        self.update_simulation_settings()
        self.update_adsb_settings()
        return

    def toggle_adsb_report(self) -> None:
        """Toggles ADS-B commandline info report"""
        self.__adsb_report = not self.__adsb_report
        return
    
    def update_render_settings(self) -> None:
        """Updates simulation render state settings"""
        self.gui_render_threshold = self.simulation_settings.gui_render_threshold
        return
    
    def update_simulation_settings(self) -> None:
        """Updates simulation physics state settings"""
        self.simulation_threshold = self.simulation_settings.simulation_threshold
        self.g_acceleration = self.simulation_settings.g_acceleration
        return
    
    def update_adsb_settings(self) -> None:
        """Updates simulation ADS-B state settings"""
        self.adsb_threshold = self.simulation_settings.adsb_threshold
        return

    def append_paused_time(self) -> None:
        """Appends time elapsed during recent pause"""
        if self.pause_start_timestamp is not None:
            self.time_paused += self.pause_start_timestamp.msecsTo(QTime.currentTime())

    def toggle_pause(self) -> None:
        """Pauses the simulation"""
        if self.is_paused:
            self.append_paused_time()
            self.is_paused = False
        else:
            if not self.is_running:
                return
            self.pause_start_timestamp = QTime.currentTime()
            self.is_paused = True
        return
    
    @property
    def collision(self) -> bool:
        """Returns collision state"""
        return self.__collision

    def register_collision(self) -> None:
        """Registers collision"""
        self.__collision = True
        return
    
    @property
    def first_cause_collision(self) -> bool:
        """Returns causing collision state"""
        return self.__first_cause_collision
    
    def toggle_first_causing_collision(self) -> None:
        """Toggles causing collision state"""
        self.__first_cause_collision = not self.__first_cause_collision
        return
    
    @property
    def second_cause_collision(self) -> bool:
        """Returns causing collision state"""
        return self.__second_cause_collision
    
    def toggle_second_causing_collision(self) -> None:
        """Toggles causing collision state"""
        self.__second_cause_collision = not self.__second_cause_collision
        return
    
    @property
    def reset_demanded(self) -> bool:
        """Returns simulation reset state"""
        with QMutexLocker(self.__mutex):
            return self.__reset_demanded

    def reset(self) -> None:
        """Resets simulation to its start state"""
        with QMutexLocker(self.__mutex):
            self.__reset_demanded = True
        return

    def apply_reset(self) -> None:
        """Sets back simulation reset state"""
        with QMutexLocker(self.__mutex):
            self.__reset_demanded = False
        return

    @property
    def gui_scale(self) -> float:
        """Returns GUI scaling factor"""
        return self.__gui_scale
    
    @gui_scale.setter
    def gui_scale(self, value : float) -> None:
        """Sets GUI scaling factor"""
        if value > 0.0:
            self.__gui_scale = value
        return
