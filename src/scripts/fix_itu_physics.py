import re

with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/s500.itu.urdf', 'r') as f:
    content = f.read()

# 1. Zero out child masses
content = content.replace('<mass value="0.12307655777311156"/>', '<mass value="0.0001"/>')
content = content.replace('<mass value="0.05057573328088262"/>', '<mass value="0.0001"/>')

# 2. Fix child inertias to prevent physics explosions
content = content.replace('ixx="1.4e-05" iyy="1.2e-05" izz="1.4e-05" ixy="-0.0" iyz="0.0" ixz="0.0"', 'ixx="0.000001" iyy="0.000001" izz="0.000001" ixy="0.0" iyz="0.0" ixz="0.0"')
content = content.replace('ixx="1.4e-05" iyy="1.2e-05" izz="1.4e-05" ixy="-0.0" iyz="-1e-06" ixz="-0.0"', 'ixx="0.000001" iyy="0.000001" izz="0.000001" ixy="0.0" iyz="0.0" ixz="0.0"')
content = content.replace('ixx="1.4e-05" iyy="1.2e-05" izz="1.4e-05" ixy="0.0" iyz="-0.0" ixz="-0.0"', 'ixx="0.000001" iyy="0.000001" izz="0.000001" ixy="0.0" iyz="0.0" ixz="0.0"')
content = content.replace('ixx="8e-05" iyy="0.000194" izz="0.000114" ixy="0.0" iyz="0.0" ixz="-9.4e-05"', 'ixx="0.000001" iyy="0.000001" izz="0.000001" ixy="0.0" iyz="0.0" ixz="0.0"')
content = content.replace('ixx="1.5e-05" iyy="0.000193" izz="0.000179" ixy="-1e-05" iyz="-3e-06" ixz="-4.9e-05"', 'ixx="0.000001" iyy="0.000001" izz="0.000001" ixy="0.0" iyz="0.0" ixz="0.0"')
content = content.replace('ixx="0.000157" iyy="0.000189" izz="4.2e-05" ixy="1.3e-05" iyz="2.7e-05" ixz="-7.4e-05"', 'ixx="0.000001" iyy="0.000001" izz="0.000001" ixy="0.0" iyz="0.0" ixz="0.0"')
content = content.replace('ixx="0.000144" iyy="0.000191" izz="5.2e-05" ixy="1.1e-05" iyz="1.9e-05" ixz="-8.3e-05"', 'ixx="0.000001" iyy="0.000001" izz="0.000001" ixy="0.0" iyz="0.0" ixz="0.0"')

# 3. Set exact base_link mass to 1.477 (matching hector_quadrotor exactly)
content = content.replace('<mass value="1.5"/>', '<mass value="1.477"/>')

# 4. Remove fake kt km and empty topics correctly
content = re.sub(r'<k_t>.*?</k_t>', '', content)
content = re.sub(r'<k_m>.*?</k_m>', '', content)
content = re.sub(r'<!-- İşte sihirli değnek.*', '', content)

with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/s500.itu.urdf', 'w') as f:
    f.write(content)
