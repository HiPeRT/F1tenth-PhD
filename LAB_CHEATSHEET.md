# Lab cheatsheet

## Run the simulator

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

## Use the Rviz2 tool

To "see" if the system is working properly you use the /rviz2/ tool. Open a new terminal, setup the environment, and then run the tool.
```
$ source install/setup.bash
$ rviz2
```

Once you are done, properly configure the tool by navigating "File -> Open config", and opening the file <i>/home/ubuntu/sim_ws/src/f1tenth_gym_ros/config/rviz/gym_bridge.rviz</i>

## Run a simple "keyboard" application (Teleop)

Once you run the simulator, you can run a simple demo application that lets you move the car using your keyboard.
The application comes with the simulator packages. So, to run it you must open a new terminal, set up your environment as you previously did, and run it
```
$ source install/setup.bash
$ ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Run an application (Pure pursuit or Follow-the-gap)

We assume all applications are installed in the /home/ubuntu/Code folder, so this tutorial is specific to this folder.

You shall run the simulator and Rviz2, as previously explained.

Then, within a new terminal you can setup a new enviroment as follows:
```
$ source /opt/ros/humble/setup.bash
```

Then move to the node directory (say, Pure pursuit)
```
$ cd /home/ubuntu/Code/pure_pursuit_example
```

Build...
```
$ colcon build
$ source install/setup.bash
```

And finally run your node. 

For the <i>Pure pursuit</i>
```
$ ros2 run control_node control_node
```

For the <i>Follow-the-gap</i>
```
$ ros2 launch follow_the_gap follow_the_gap_launch.py
```

## Run an empty ROS node application ("Control node")

You shall run the simulator and Rviz2, as previously explained.

Then, within a new terminal you can setup a new enviroment as follows:
```
$ source /opt/ros/humble/setup.bash
$ cd /home/ubuntu/Code
$ colcon build
$ source install/setup.bash
$ ros2 control_template control_template
```
