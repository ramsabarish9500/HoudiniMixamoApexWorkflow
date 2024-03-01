# Houdini Mixamo to Apex Workflow
 Simple Automated workflow for implementing Mixamo animations and characters in Houdini APEX flow.

# WorkFlow
The HDA and code will create basic workflow which needs to be modified as per requirement. This is just a mere skeleton

Electra Base Rig is used as a reference for the workflow.
For more info see: https://www.sidefx.com/contentlibrary/electra-rig/
Mixamo rigs are first mapped and renamed with respect to electra rig. Captured weight mappings are also renamed. 
Guide Skeletons are created based on the remapped names.(Non Destructive)
Base Apex Rig is then created and the motionclips are retargetted.

Python Tool is used to streamline the workflow.
Character and animations can be selected within the python plugin. Multiple Animations can be stacked up or looped via plugin.
Previewing the stacked motion clips are available and complete apex workflow can be generated from the plugin itself

# Disclaimer
I'm not a rigger myself. I have reused the Apex Component Scripts from the electra rig example.

# HDA Descriptions
