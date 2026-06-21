# Lab cheatsheet

Start the terminal. You shall work from within the /home/ubuntu/sim_ws folder, so CD into it
```
$ cd sim_ws
```

Then, run setup scripts to prepare your environment for execution
```
$ source install/setup.bash
```

The simulator runs within a container (i.e., a "safe" software environment). You can run this simple script to run it
```
$ ./src/f1tenth_gym_ros/scripts/run_sim_containerized.sh
```

Once you run the simulator, you can run a simple demo application that lets you move the car using your keyboard. To do so, you must open a new terminal, set up your environment as you previously did, and run it
```
$ source install/setup.bash
$ ros2 run teleop_twist_keyboard teleop_twist_keyboard
```


To "see" if the system is working properly you use the /rviz2/ tool. Open a new terminal, setup the environment, and then run the tool.
```
$ source install/setup.bash
$ rviz2
```

Once you are done, properly configure the tool by navigating "File -> Open config", and opening the file <i>/home/ubuntu/sim_ws/src/f1tenth_gym_ros/config/rviz/gym_bridge.rviz</i>
