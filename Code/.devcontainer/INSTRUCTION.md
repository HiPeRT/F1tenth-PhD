# Run these commands on the host machine to add docker permissions to use display
sudo usermod -aG docker $USER
xhost +local:docker 2>/dev/null
newgrp docker