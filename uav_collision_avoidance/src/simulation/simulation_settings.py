"""Simulation settings"""

from PySide6.QtCore import QSize

class SimulationSettings:
    """Settings for the simulation"""

    screen_resolution : QSize
    resolution : tuple
    g_acceleration : float = 9.81
    simulation_frequency : float = 100.0
    simulation_threshold : float = 1000.0 / simulation_frequency
    gui_render_frequency : float = 100.0
    gui_render_threshold : float =  1000.0 / gui_render_frequency
    adsb_threshold : float = 1000.0

    @classmethod
    def __init__(cls) -> None:
        """Initialises Settings using screen resolution"""
        cls.resolution = (int(cls.screen_resolution.width() * 0.6), int(cls.screen_resolution.height() * 0.75))
    
    @classmethod
    def set_resolution(cls, width, height) -> None:
        """Sets the resolution"""
        cls.resolution = (width - 10, height - 10)
        return
    
    @classmethod
    def get_resolution(cls) -> tuple[float, float]:
        """Gets the resolution"""
        return (cls.resolution[0], cls.resolution[1])

    @classmethod
    def set_simulation_frequency(cls, simulation_frequency) -> None:
        """Sets the simulations per second"""
        cls.simulation_frequency = simulation_frequency
        return
