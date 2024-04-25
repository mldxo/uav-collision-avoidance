# UAV Collision Avoidance

Python project regarding implementation of UAV physics and collision detection/avoidance algorithms.
- [Github](https://github.com/mldxo/uav-collision-avoidance)
- [PyPi](https://pypi.org/project/uav-collision-avoidance)

## Research work

### Introduction

UAV Collision Avoidance is my Bachelor's thesis project meeting problem of UAVs safe cooperation in the 3D space. Project implements functional physics calculations, scalable GUI, realistic ADS-B probable collision avoidance systems and on-board flight planning. Application offers multithreaded realtime simulation presenting simulated aircrafts as well as linearly prerendered simulation allowing for quick algorithm effectiveness testing. The project is based on two research papers[^4][^5].

### Premises

1. System Definition: The system is defined as a 3-dimensional (3D) space using an XYZ coordinate system. X and Y represent a flat horizontal plane, while Z represents height above sea level.
2. Physics Simulation: Physics are simulated by differentiating parts of the second according to appropriate formulas. The physics of Unmanned Aerial Vehicles (UAVs) are considered relative to the Earth's frame, separated from the aircraft's frame and wind relative frame. 3D space is flat, and the Earth's curvature is not considered. Gaining or losing altitude preserves the aircraft's speed.
3. Aircraft Characteristics: The aircraft are considered Horizontal Take-off and Landing (HTOL) drones. They can only move in the direction of their speed vectors. The form of the aircraft is approximated to a simple solid sphere.
4. Environment: The space is shared by two or three UAVs. There are no other objects or wind gusts assumed in this environment.
5. Aerodynamics: No aerodynamic lift force is assumed at this moment. When turning, aircraft always take the maximum angle change that physics allow, respecting mass inertia. The angles are not approximated to meet exact courses.
6. Units of Measurement: The default distance units are meters (m), speed is measured in meters per second (m/s), and frame times are represented in milliseconds (ms).

### Algorithms

Both collision detection and avoidance algorithms rely on geometrical approach. They were presented in referenced paper[^4]. Collision detection differentiates between collision and head-on collision. The second one applies when UAVs have no distance between their projected center of masses collision, and the first one when it is every other type of contact.

## Python Project

### Technologies

Python3[^1] project is wrapped as a PyPi package[^2]. PySide6[^3] (Qt's Python Qt6 library) was used for GUI implementation.

### Structures

Application is built based on two main object types, simulation and aircraft. Simulation is created up to initial settings, allowing for concurrent realtime variant and linear prerendering. Aircraft consists of two elements, physical representation of the UAV and Flight Control Computer, which is controlled by the physics thread. Research among the UAV systems was possible thanks to second paper[^5].

### App arguments

There are three possible arguments at the moment:
- realtime - runs GUI application with realtime simulation
- prerender - runs physical simulation
- tests - runs full tests with comparison of using and not using collision avoidance algorithm

App defaults to realtime simulation.

### Key shortcuts

> [!NOTE]
> Aircraft 0 is the first one, Aircraft 1 is the second one.

There are several key shortcuts for realtime version of the app that allow full-scale testing.

- Left mouse click - appends click location to the top of destination list of Aircraft 0
- Right mouse click - adds click location to the end of destination list of Aircraft 0
- Middle mouse click (scroll click) - teleports Aircraft 0 to the click location
- Mouse wheel - zooms in/out the simulation render smoothly
- Plus/minus keys (+/-) - zooms in/out the simulation render quickly
- Arrow keys (↑ ↓ → ←) - moves the view
- F1 key - toggles ADS-B Aircraft 0 info reporting
- F2/F3 keys - speed up/down target speed of Aircraft 0
- N key - toggles Aircraft 0/1 view following (default off)
- M key - switches between Aircraft 0/1 view following (default 0)
- O key - toggles Aircraft 0 targeting Aircraft 1's speed vector (default off)
- P key - toggles Aircraft 1 targeting Aircraft 0's speed vector (default off)
- T key - toggles collision avoidance maneuvering (default off)
- WSAD keys - sets course for Aircraft 0 - 0, 180, 270, 90 degrees respectively
- R - resets simulation to start state
- Slash key (/) - pauses physics simulation
- Escape key (Esc) - closes and ends simulation

### Install

Use `pip install uav-collision-avoidance` to install the app and run one of the following:
- uav-collision-avoidance
- uav-collision-avoidance realtime
- uav-collision-avoidance prerender
- uav-collision-avoidance tests

### Build

Build it by cloning the repo and running the following commands:

<p align="left">
    <img width="30px" alt="Bash" style="padding-right:10px;" src="https://skillicons.dev/icons?i=bash" />
</p>

```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py [argument]
```

<p align="left">
    <img width="30px" alt="Powershell" style="padding-right:10px;" src="https://skillicons.dev/icons?i=powershell" />
</p>

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py [argument]
```

### Remarks

3-dimensional (3D) world is projected on 2D screen by flattening height (z coordinate). On the program start, the view is centered on the first aircraft. The view can be moved with arrow keys.

One coding convention is not preserved in the scope of the project. Qt's methods are CamelCase formatted and the rest is default Python naming convention including snake_case for variable and member names.

## Current Work / TODOs

- [x] Reimplement safe zone
- [x] Head-on collision avoidance
- [x] Symmetrical bank (roll) during turn, no angle approaximation
- [x] Altitude change with symmetrical command
- [ ] Generating test cases and batch loading
- [ ] Test cases comparison
- [x] Aircraft 0 manual control override
- [ ] Flight control computer angle optimization
- [ ] Centered view optimization
- [ ] Documentation

## Authors

- [Miłosz Maculewicz](https://github.com/mldxo)

## References

All used references are listed below.

[^1]: [Python3](https://www.python.org/)
[^2]: [PyPi](https://pypi.org/)
[^3]: [PyQt6](https://doc.qt.io/qtforpython-6/)
[^4]: [UAV Collision Avoidance Based on Geometric Approach](https://ieeexplore.ieee.org/document/4655013/)
[^5]: [Energy Efficient UAV Flight Control Method in an Environment with Obstacles and Gusts of Wind](https://www.mdpi.com/1638452/)
