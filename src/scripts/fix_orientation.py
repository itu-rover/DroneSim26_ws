import re

# 1. Update URDF
with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/s500.itu.urdf', 'r') as f:
    content = f.read()

if '<link name="drone_body">' not in content:
    # Replace link name="base_link" -> drone_body
    content = content.replace('<link name="base_link">', '<link name="drone_body">')
    # Replace parent link="base_link" -> drone_body
    content = content.replace('parent link="base_link"', 'parent link="drone_body"')
    
    new_base_link = """
<link name="base_link">
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="0.001"/>
    <inertia ixx="0.00001" iyy="0.00001" izz="0.00001" ixy="0.0" iyz="0.0" ixz="0.0"/>
  </inertial>
</link>

<joint name="base_to_drone_body" type="fixed">
  <!-- POSITIVE 90 degrees roll maps CAD Y-up to Gazebo Z-up! -->
  <origin xyz="0 0 0" rpy="1.57079632679 0 0" />
  <parent link="base_link" />
  <child link="drone_body" />
</joint>
"""
    # Insert right before <link name="drone_body">
    content = content.replace('<link name="drone_body">', new_base_link + '<link name="drone_body">')

    # Make sure we don't mess up the plugin's bodyName (it should stay base_link)
    # The replacement above changes everything. Let's fix the plugin back if we accidentally changed it.
    # Actually 'parent link="base_link"' was for joints. 
    # Did I replace bodyName? No, I did not replace 'base_link' globally, only specific tags.
    # But wait, plugin has <bodyName>base_link</bodyName>. It's untouched.
    # Also <frameId>base_link</frameId>. Also untouched.

    with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/s500.itu.urdf', 'w') as f:
        f.write(content)

# 2. Update Gazebo tags
with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/itu_s500.gazebo', 'r') as f:
    g_content = f.read()
if 'reference="base_link"' in g_content:
    g_content = g_content.replace('reference="base_link"', 'reference="drone_body"')
    with open('/home/bakyolal/DroneSim_ws/src/itu-s500/urdf/itu_s500.gazebo', 'w') as f:
        f.write(g_content)

