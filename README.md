# FERPanda-IAI
# Franka Emika Panda Arm Configuration for ROS2

Welcome to the GitHub repository for configuring the Franka Emika Panda robot for ROS2. This repository contains all necessary files, instructions, and scripts to get your Panda arm up and running with ROS2.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
    1. [Network Requirements](#network)
    2. [Realtime Kernel Setup](#rtkernel)
    3. [CPU Requirements](#cpuscaling)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Troubleshooting](#troubleshooting)

## 1. Overview

This repository is dedicated to setting up and configuring the Franka Emika Panda arm for use with ROS2.
The Franka Emika Panda robot is a 7-axis robot arm, it offers a 3 kg payload and 850 mm of reach. The repeatability of the Franka Emika Panda robot is 0.1 mm and the robot weight is approximately 18 kg.
Common applications of the Franka Emika Panda include: Dispensing, Remote TCP, Welding and ROS2 provides a powerful framework for developing robot software.

In order to work with ROS2 in Panda arm, we need to make sure that FCI(Franka Control Interface) mode is activated. The Franka Control Interface (FCI) offers a rapid and direct low-level bidirectional link to the Arm and Hand. It supplies the robot's current status and allows for direct control from an external workstation PC connected via Ethernet.

## 2. Prerequisites

The given repo was implemented and tested on system with following specifications:

- **Operating System**: Ubuntu 22.04 or later with PREEMPT_RT patched kernel(Strongly recommended)
- **ROS2 Distribution**: ROS2 Humble
- **Robot version**: 4.2.2 
- **Franka Emika Panda**: Access to the Panda robot arm hardware
- **Franka ROS2 Packages**: Clone or download the necessary ROS2 packages for Franka
- **libfranka library version**: 0.9.2
  
Given that the robot transmits data at a frequency of 1 kHz, it's crucial to configure the workstation PC to minimize latencies. For instance, we recommend ['disabling CPU frequency scaling'](https://frankaemika.github.io/docs/troubleshooting.html#disabling-cpu-frequency-scaling). Other potential optimizations will vary based on your specific system.

`libfranka` or C++ implementation for client side of FCI, it establishes network communication with Control and its API documentation is available on [here.](https://frankaemika.github.io/libfranka/)

# Network

It is advised to connect your Workstation PC directly to the base of Panda arm and avoid any intermediate device (e.g. Network Switch) as such indirect connection can lead to delay, jitter and packet loss.

# Realtime Kernel Setup

It is strongly recommended to setup realtime kernel in order to work with Franka Emika Panda arm. Here, Steps are given to set realtime kernel to workstation PC.

1. Install dependencies

   ```bash
   sudo apt-get build-dep linux
   sudo apt-get install libncurses-dev flex bison openssl libssl-dev dkms libelf-dev libudev-dev libpci-dev libiberty-dev autoconf fakeroot
   ```
2. Decide which kernel version to use. It is advised to choose the kernel version which is closest to your current kernel version.

   To find kernel version you are using currently, use following command:

   ```bash
   uname -r
   ```
3. Now, check for realtime patches available for selected kernel version, check [here](https://www.kernel.org/pub/linux/kernel/projects/rt/).

    Go to the folder where you want to download source files for Kernel. Let's download source files using **curl**,
    
    ```bash
    curl -SLO https://www.kernel.org/pub/linux/kernel/v6.x/linux-6.8.2.tar.xz
    curl -SLO https://www.kernel.org/pub/linux/kernel/projects/rt/6.8/patch-6.8.2-rt11.patch.xz
    ```

    Now, Decompress source files using following command,
   
    ```bash
    xz -d *.xz
    ```

4. Compiling the Kernel
  Once you are sure the files were downloaded properly, you can extract the source code and apply the patch:
 
   ```bash
   tar xf linux-*.tar
   cd linux-*/
   patch -p1 < ../patch-*.patch
   ``` 
5. Make a new .config file and copy old configuration.
   
   ```bash
   cp /boot/config-5.4.0-54-generic .config
   yes '' | make oldconfig
   ```
   Then we need to enable rt_preempt in the kernel with:

   ```bash
   make menuconfig
   ```
   In a pop-up window, set the following.
   ```
    # Enable CONFIG_PREEMPT_RT
     -> General Setup
      -> Preemption Model (Fully Preemptible Kernel (Real-Time))
       (X) Fully Preemptible Kernel (Real-Time)
    
    # Enable CONFIG_HIGH_RES_TIMERS
     -> General setup
      -> Timers subsystem
       [*] High Resolution Timer Support
    
    # Enable CONFIG_NO_HZ_FULL
     -> General setup
      -> Timers subsystem
       -> Timer tick handling (Full dynticks system (tickless))
        (X) Full dynticks system (tickless)
    
    # Set CONFIG_HZ_1000 (note: this is no longer in the General Setup menu, go back twice)
     -> Processor type and features
      -> Timer frequency (1000 HZ)
       (X) 1000 HZ
    
    # Set CPU_FREQ_DEFAULT_GOV_PERFORMANCE [=y]
     ->  Power management and ACPI options
      -> CPU Frequency scaling
       -> CPU Frequency scaling (CPU_FREQ [=y])
        -> Default CPUFreq governor (<choice> [=y])
         (X) performance
    ```
    In the end, Save and exit the given .config fil and build the kernel which will take around 30-45 minutes.
    
    ```bash
    make - `nproc`
    ```
    ---
    **NOTE:** At the time of compilation, if you get the following error:
        
    ```bash
    make[4]: *** No rule to make target 'debian/canonical-certs.pem', needed by 'certs/x509_certificate_list'.  Stop.
    ```

    You can solve it by making following changes in .config file   
    ```bash 
    CONFIG_SYSTEM_TRUSTED_KEYS="debian/canonical-certs.pem"
    CONFIG_SYSTEM_REVOCATION_KEYS="debian/canonical-revoked-certs.pem"
    CONFIG_DEBUG_INFO_BTF=y
    ```
    with, 
    ```bash
    CONFIG_SYSTEM_TRUSTED_KEYS=""  
    CONFIG_SYSTEM_REVOCATION_KEYS=""  
    CONFIG_DEBUG_INFO_BTF=n      
    ```
    and following commands in terminal,  
    ```bash
    scripts/config --disable SYSTEM_TRUSTED_KEYS
    scripts/config --disable SYSTEM_REVOCATION_KEYS
    ```
    and then compile the kernel again.

    ---    
    After compiling the kernel, we can install the kernel with:
    ```bash
    sudo make install
    ```
    Add successful compilation and installation of kernel, provide realtime access to the user by adding them to rt group

    ```bash
    sudo addgroup rt
    sudo usermod -a -G rt $(whoami)
    ```
   Afterwords, add following limits to `rt` group in `/etc/security/limits.conf`:

   ```bash
   @rt soft rtprio 99
   @rt soft priority 99
   @rt soft memlock 102400
   @rt hard rtprio 99
   @rt hard priority 99
   @rt hard memlock 102400 
   ```
   and then reboot your PC with,

   ```bash
   reboot
   ```
## Installation

Follow these steps to install the necessary packages and dependencies:

1. **Update your system:**
    ```bash
    sudo apt update
    sudo apt upgrade
    ```

2. **Install ROS2:**
    Follow the official [ROS2 installation guide](https://docs.ros.org/en/humble/Installation/Alternatives/Ubuntu-Development-Setup.html).

3. **Clone this repository:**
     Clone this repository in your workspace's 'src' folder
    ```bash
    git clone https://github.com/mitsav01/FERPanda-IAI.git
    cd FERPanda-IAI
    ```

4. **Install dependencies:**
    ```bash
    rosdep update
    rosdep install --from-paths src --ignore-src -r -y
    ```

5. **Build the workspace:**
    ```bash
    colcon build --mixin Release -DFranka_DIR:PATH=/path/to/libfranka/build
    source install/setup.bash
    ```
    If you don't want to write path of `libfranka` library everytime you build the workspace, you can modify your `.bashrc` configuration by adding it to `LD_LIBRARY_PATH` like this:

   ```
   export LD_LIBRARY_PATH=/home/mitesh/libfranka/build:$LD_LIBRARY_PATH
   ```
## Usage

In order to work with robot, we should know IP address to establish a connection with robot. To check that please take following steps:

1. **Connect LAN cable coming from Robotic arm directly to your PC and visit following web-address in your web-browser:**
   ```
   robot.franka.de
   ```
    If you are logging in for the first time, you should trust the website certificate and `Desk` interface looks like following:

    ![Homepage](https://github.com/mitsav01/FERPanda-IAI/blob/965b8312fa0bbb1a35fc18bcdd5559481de5bc93/images/Homepage.png) 

   Now, On top right corner of `Desk` interface, there would be a drop-down menu;Open Settings and Go to Dashboard.
   You will see something like this there.
    ![Dashboard](https://github.com/mitsav01/FERPanda-IAI/blob/965b8312fa0bbb1a35fc18bcdd5559481de5bc93/images/Dashboard.png) 
   Inside Network, IP address of Shop Floor is `<fci-ip>` in our case.

   If you do fresh bootup of the robot and open the `Desk` interface, you will see the **Robot Status** in bottom Right corner as following,
    ![jointslocked](https://github.com/mitsav01/FERPanda-IAI/blob/2f6392bfa50f41be47bb091487f4846a55a285aa/images/jointlocked.png)

   In order to work with robot, we can unlock the joints by selecting **Unlock symbol** inside **Joints** panel on right side of `Desk` interface and select **Open** from "Open fail safe locking system. Robot will initialize itself and unlock joints.

3. **ROS2 Interface:**

    If we want to work with ROS2 and Panda arm, We should enable FCI in `Desk` interface. For that go to Homepage of `Desk` interface and Click on Activate FCI inside the settings.
    ![FCI](https://github.com/mitsav01/FERPanda-IAI/blob/965b8312fa0bbb1a35fc18bcdd5559481de5bc93/images/FCI-activation.png) 


4. **Source the workspace:**
    It is really important to source the workspace everytime after compilation in order to make effect of changes. For that, go to your workspace in terminal and type following:
    ```bash
    source install/setup.bash
    ```

2. **Launch the robot:**
    This repo contains some example which we can use to see how robot moves. We can do it by following some steps,
    1.Open terminal and source the workspace and write following command:
    ```bash
    ros2 launch franka_bringup franka.launch.py robot_ip:=<fci-ip>
    ```
    Now, Our robot is activated if you want to visualise the robot in Rviz2, you can do it with following command
    ```bash
    ros2 launch franka_bringup franka.launch.py robot_ip:=<fci-ip> use_rviz:=true
    ```
    If you want to move the robot with some example scripts, Open a new terminal and write rqt as following,
    ```bash
    rqt
    ```
    You will have a new pop-up window, Go to **Plugins>Robot Tools>Controller manager**
    ![rqt](https://github.com/mitsav01/FERPanda-IAI/blob/f87e905f792bc7c68b1a6cb62be24d3212d8443b/images/rqt.png)

   Inside Controller Manager Plugin, Choose the namespace as **/controller_manager**, You will see some examples as following
   
    ![controllermanager](https://github.com/mitsav01/FERPanda-IAI/blob/f87e905f792bc7c68b1a6cb62be24d3212d8443b/images/controllermanager.png)

   Just Click on the example you want to run and select **Load,Configure and Activate** and you can see some moments as per the examples in Robot.

4. **Control the robot:**
   If you want to control the robot as per your desired movements, we can use MoveIt2 specific launch by giving following commands,
   Open the new terminal,
    ```bash
    ros2 launch franka_moveit_config moveit.launch.py robot_ip:=<fci-ip>
    ```
   You will have a new Rviz2 pop-up window like this with activated **MotionPlanning**:
   ![moveit](https://github.com/mitsav01/FERPanda-IAI/blob/f87e905f792bc7c68b1a6cb62be24d3212d8443b/images/moveit.png)
   If you want to give robot some movements, just move the rings which is around the robot end-effector and select **Plan & Execute** inside `Commands` panel of **MotionPlanning** window,
   If you want to rotate end-effector of Robot, select `panda_manipulator` inside `Query` panel of **MotionPlanning** windows and you will notice an additional ring around end-effector. You can rotate an end-effector by moving that ring and press **Plan & Execute**.
   If you want to control the gripper, you can select `hand` inside `Query` panel of **MotionPlanning** window and use **Open** and **Close** command in `Goal State`. You can notice opening and closure of gripper.



## Troubleshooting

This repo contains some functionality to recover from error generated by some motions which can damage joints of the robot. At the time of these errors, robot will stop by itself as a precaution and you will see following error in Terminal,

**1. `libfranka` error**

```
[ros2_control_node-5] libfranka: Move command aborted: motion aborted by reflex! ["cartesian_reflex"]
```
or any other arguments from `libfranka`, 
we can use following ros2 command to get rid of these errors,
```bash
ros2 service call /error_recovery_service_server/error_recovery franka_msgs/srv/ErrorRecovery "{}"
```
If there is really any error from `libfranka`, you will get following response and your robot will move to previous safe position.
```
requester: making request: franka_msgs.srv.ErrorRecovery_Request()

response:
franka_msgs.srv.ErrorRecovery_Response(success=True, error='')

```
and inside the terminal where **Moveit2** launch file is running, you will following response
```
[ros2_control_node-5] [INFO] [1724842814.870647908] [error_recovery_service_server]: Successfully recovered from error.
```
You can double check that by giving the above command again and verify if you have following response

```
requester: making request: franka_msgs.srv.ErrorRecovery_Request()

response:
franka_msgs.srv.ErrorRecovery_Response(success=False, error='No errors')
```
and inside the terminal, it will reflect as

```
requester: making request: franka_msgs.srv.ErrorRecovery_Request()

response:
franka_msgs.srv.ErrorRecovery_Response(success=False, error='No errors')
```
**2. [ros2_control_node-5] [WARN] [1724844087.268810248] [controller_manager]: Waiting for data on 'robot_description' topic to finish initialization**

If you launch the moveit launch file as given in **Control the robot** section and encounter above error and your Rviz2 terminal looks like this:
![controllernotavailable](https://github.com/mitsav01/FERPanda-IAI/blob/2f6392bfa50f41be47bb091487f4846a55a285aa/images/controllernotready.png)
You might have forgot to **activate fci** in `Desk` interface or check the if your LAN cables are connected properly.

If you encounter any other issues, please refer to the following resources:

- [Franka Emika Documentation](https://frankaemika.github.io/docs/)
- [ROS2 Documentation](https://docs.ros.org/en/humble/)
- [ROS2 Community](https://discourse.ros.org/)


> Note: If you notice some mistakes and or some changes please open an issue.
