# Houdini Mixamo to Apex Workflow
 Simple Automated workflow for implementing Mixamo animations and characters in Houdini APEX based workflow.

# WORKFLOW
The HDA's and python plugin will create basic workflow which needs to be modified as per requirement. This is just a mere skeleton

Electra Base Rig is used as a reference for the workflow.
For more info see: https://www.sidefx.com/contentlibrary/electra-rig/ .
Mixamo rigs are first mapped and renamed with respect to electra rig. Captured weight mappings are also renamed. 
Guide Skeletons are created based on the remapped names.(Non Destructive)
Base Apex Rig is then created and the motionclips are retargetted.

Python Tool is used to streamline the workflow.
Character and animations can be selected within the python plugin. Multiple Animations can be stacked up or looped via plugin.
Previewing the stacked motion clips are available and complete apex workflow can be generated from the plugin itself

# DISCLAIMER
I'm not a rigger. I have reused the Apex Component Scripts from the electra rig example.

# HDA DESCRIPTIONS
   # MixamoNameRemap
     Make's use of the map points sop to map the names between electra rig and mixamo rig.
     Rename the Captured Atrributes in Captured geometry
     Cleans the "name" attribute
   # MixamoApexConfigurator
     Create tags for Apex. Inspired from the electra rig example
     Create a Guide Skeleton procedurally with the remapped names. Modify the Guide skeletons if required.(EG: ArmPole Spacing)
   # ApexBipedRig
     Uses the electra rig and reimplements for mixamo characters
   #  ApexTransferMixamoAnimation
     Retarget the animation clips to new apex based mixamo character
     New animation will be added to the apex scene

# HOW TO SETUP
  # STEP 1:
    Install all the 4 hda's present inside the hda folder.
    Eg: Assets --> Install Digital Asset Library --> Select all 4 HDA files --> Install
  # STEP 2:
    Create a New Tool in any shelf of choice. Name it accordinglys. In the Script Tab Copy the code from "MixamoApexConverterTool.py" and paste it and accept.
    Eg: In Animatin Shelf --> Right Click --> New Tool --> Script(TAB) --> Paste the Code --> Accept
