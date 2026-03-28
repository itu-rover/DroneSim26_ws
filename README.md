# DroneSim26_ws
Simulation for drone scripts and controls.

# Gazebo Simulation
Launch the simulation environment:

```
roslaunch launch fly_my_drone.launch
```

Launch the controller:
```
roslaunch launch xbox_control.launch
```
For starting the motors:
```
rosservice call /enable_motors true
```

The Controller Schema:

# L1: Lock button

# L3: 
# ↑ ↓ on Z axis
# ↺ ↻ on YAW 

# R3:
# ↑ ↓ on X axis
# ← → on Y axis
