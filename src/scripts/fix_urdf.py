import re

with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/s500.itu.urdf', 'r') as f:
    content = f.read()

# Replace link name="base_link" with link name="drone_body"
content = content.replace('<link name="base_link">', '<link name="drone_body">')
# Replace parent link="base_link" with parent link="drone_body"
content = content.replace('parent link="base_link"', 'parent link="drone_body"')

# Now insert the new base_link and the fixed joint connecting base_link to drone_body
new_base_link = """
<link name="base_link">
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="0.001"/>
    <inertia ixx="0.00001" iyy="0.00001" izz="0.00001" ixy="0.0" iyz="0.0" ixz="0.0"/>
  </inertial>
</link>

<joint name="base_to_drone_body" type="fixed">
  <origin xyz="0 0 0" rpy="-1.57079632679 0 0" />
  <parent link="base_link" />
  <child link="drone_body" />
</joint>
"""

# Insert right after the plugin block (which ends with </gazebo>)
# Wait, plugin block is for quadrotor_propulsion which uses <bodyName>base_link</bodyName> -- that should remain base_link!
pos = content.find('<link name="drone_body">')
content = content[:pos] + new_base_link + content[pos:]

with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/s500.itu.urdf', 'w') as f:
    f.write(content)

# Fix itu_s500.gazebo
with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/itu_s500.gazebo', 'r') as f:
    gazebo_content = f.read()
gazebo_content = gazebo_content.replace('reference="base_link"', 'reference="drone_body"')
with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/itu_s500.gazebo', 'w') as f:
    f.write(gazebo_content)
