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
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

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

**libfranka** or C++ implementation for client side of FCI, it establishes network communication with Control and its API documentation is available on [here.](https://frankaemika.github.io/libfranka/)

# Network*

It is advised to connect your Workstation PC directly to the base of Panda arm and avoid any intermediate device (e.g. Network Switch) as such indirect connection can lead to delay, jitter and packet loss.

# Realtime Kernel Setup*

It is strongly recommended to setup realtime kernel in order to work with Franka Emika Panda arm. Here, Steps are given to set realtime kernel to workstation PC.

1. Install dependencies

   ```bash
   sudo apt-get install build-essential bc curl ca-certificates gnupg2 libssl-dev lsb-release libelf-dev bison flex dwarves zstd libncurses-dev
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
    colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release -DFranka_DIR:PATH=/path/to/libfranka/build
    source install/setup.bash
    ```

## Usage

To start using the Panda arm with ROS2, follow these steps:

1. **Source the workspace:**
    ```bash
    source install/setup.bash
    ```

2. **Launch the robot:**
    ```bash
    ros2 launch franka_bringup franka.launch.py robot_ip:=<fci-ip>
    ```

3. **Control the robot:**
    Open the new terminal,
   ```bash
    ros2 launch franka_moveit_config moveit.launch.py robot_ip:=<fci-ip>
    ```

## Examples

This repository includes example scripts to help you get started with the Panda arm. Examples are located in the `examples` directory and include basic motion commands, trajectory planning, and more.

## Troubleshooting

If you encounter any issues, please refer to the following resources:

- [Franka Emika Documentation](https://frankaemika.github.io/docs/)
- [ROS2 Documentation](https://docs.ros.org/en/humble/)
- [ROS2 Community](https://discourse.ros.org/)




* This readme file is still in progress.
