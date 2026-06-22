FROM ubuntu:jammy
LABEL maintainer "Francesco Moretti"

ARG USER=default_user
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG ROS_DISTRO=humble

# Install ROS2
# Set local
ENV DEBIAN_FRONTEND noninteractive

RUN apt update && apt install locales \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && export LANG=en_US.UTF-8

# Setup sources
# RUN apt-get install software-properties-common -y \
#     && add-apt-repository universe 
RUN apt install software-properties-common -y\
    && add-apt-repository universe
    
RUN apt-get install software-properties-common can-utils net-tools iproute2 -y 

RUN apt-get update && apt-get install curl -y \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt-get update \ 
    && apt-get install ros-${ROS_DISTRO}-desktop -y \
    && apt-get install ros-dev-tools -y
    
RUN apt-get install -y ros-${ROS_DISTRO}-tf* ros-${ROS_DISTRO}-pcl-conversions \
    ros-${ROS_DISTRO}-ackermann-msgs ros-${ROS_DISTRO}-rmw-fastrtps-cpp ros-${ROS_DISTRO}-gps-msgs \
    ros-${ROS_DISTRO}-udp-msgs ros-${ROS_DISTRO}-diagnostic-updater ros-${ROS_DISTRO}-laser-proc
RUN apt-get install bash-completion -y



# Create the user
RUN groupadd --gid $USER_GID $USER \
    && useradd --uid $USER_UID --gid $USER_GID -m $USER \
    && usermod --shell /bin/bash  $USER \
    && usermod -aG dialout $USER \
    && usermod -aG video $USER

# Add sudo support
RUN apt-get update \
    && apt-get install -y sudo \
    && usermod -aG sudo $USER \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER $USER

# Install clang
RUN sudo apt-get install clang clang-format -y

RUN sudo apt-get install libasio-dev

# Install python-can for CAN bridge testing
RUN sudo apt-get install python3-pip -y
RUN sudo pip install python-can

# Install livox sdk
WORKDIR /tmp
RUN git clone https://github.com/Livox-SDK/Livox-SDK2.git
WORKDIR /tmp/Livox-SDK2/
RUN mkdir build
WORKDIR /tmp/Livox-SDK2/build
RUN cmake .. && make -j
RUN sudo make install
WORKDIR /tmp
RUN sudo rm -rf Livox-SDK2/

WORKDIR /home/$USER
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> ~/.bashrc
