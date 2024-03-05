import os 
from PySide2 import QtWidgets
from PySide2.QtWidgets import QFileDialog
from PySide2 import QtGui
from PySide2.QtCore import Qt, QAbstractItemModel, QEvent


class MixamoApexConverter(QtWidgets.QDialog):
    
    def __init__(self):
        super(MixamoApexConverter,self).__init__(hou.qt.mainWindow())
        self.initVars()
        self.initUI()

    def initVars(self):
        self.fbxFiles = []
        self.objContext = hou.node("/obj")
        self.charFile = None
        self.headerNames = ["Clip Name" ,"Loop"]
        self.geoContext = None
        self.motionClipSubnet = None
        self.hipReferenceBoneName = 'hips'
        self.locomotionJointName = None

    def initUI(self):  
        self.setWindowTitle("Mixamo Apex Converter")
        self.setMinimumWidth(500)
        self.setMinimumHeight(50)
        self.initWidgets()
        self.initLayout()
        
    def initWidgets(self):
        
        self.addAnimationsButton = QtWidgets.QPushButton("Add Animations",self)
        self.addAnimationsButton.clicked.connect(self.addAnimations)
        
        self.addCharacterButton = QtWidgets.QPushButton("Add Character",self)
        self.addCharacterButton.clicked.connect(self.addCharacter)
        
        self.previewButton = QtWidgets.QPushButton("Preview",self)
        self.previewButton.clicked.connect(self.preview)
        self.previewButton.setEnabled(False)
        
        self.apexConvertButton = QtWidgets.QPushButton("Apex Convert",self)
        self.apexConvertButton.clicked.connect(self.apexConvert)
        self.apexConvertButton.setEnabled(False)
        
        self.characterText = QtWidgets.QLineEdit()
        self.characterText.setReadOnly(True)
        
        self.tableView = QtWidgets.QTableView()
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setDragEnabled(True)
        self.tableView.setAcceptDrops(True)
        self.tableView.setDragDropOverwriteMode(False)
        
        self.tableViewModel = QtGui.QStandardItemModel()
        self.tableView.setModel(self.tableViewModel)
        self.tableViewModel.setHorizontalHeaderLabels(self.headerNames)
        self.tableViewModel.itemChanged.connect(self.onTableDataChanged)
        
    def onTableDataChanged(self):
        model = self.tableView.model()
        rowCount =  model.rowCount()
        if(rowCount > len(self.fbxFiles)):
            lastAddedItem = model.item(rowCount-1,0)
            if(lastAddedItem):
                lastAddedName = lastAddedItem.text()
                for count in range(rowCount):
                    clipName = model.item(count,0).text()
                    if(clipName == lastAddedName):
                        self.fbxFiles.append(self.fbxFiles[count])
                        break
    
    def initLayout(self):
        self.mainLayout= QtWidgets.QVBoxLayout(self)
        
        self.formLayout = QtWidgets.QFormLayout(self)
        self.mainLayout.addLayout( self.formLayout)
        self.formLayout.addRow("Character", self.characterText) 
        
        self.viewLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout( self.viewLayout)        
        self.viewLayout.addWidget( self.tableView)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.addCharacterButton)   
        self.buttonLayout.addWidget(self.addAnimationsButton)
        self.buttonLayout.addWidget(self.previewButton)  
        self.buttonLayout.addWidget(self.apexConvertButton)    
        self.mainLayout.addLayout( self.buttonLayout)
        
    def addAnimations(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter("*.fbx")
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setOptions(QFileDialog.DontUseNativeDialog)
        if dialog.exec_():
            self.fbxFiles.extend(dialog.selectedFiles())
            self.addAnimationNamesInView(dialog.selectedFiles())
    
    def addAnimationNamesInView(self, newFiles):
        for fbxFile in newFiles:
            animName = self.animationClipNameFromFile(fbxFile)
            nameItem = QtGui.QStandardItem(animName)   
            loopItem = QtGui.QStandardItem()
            loopItem.setData(0,Qt.EditRole)
            self.tableView.model().appendRow([nameItem, loopItem])
        
        model =  self.tableView.model()
        rowCount = model.rowCount()
        if(rowCount > 1):
            self.previewButton.setEnabled(True)
            if(self.charFile):
                self.apexConvertButton.setEnabled(True)

    def apexConvert(self):
        if(self.motionClipSubnet is None):
            self.preview()
        
        charNode = self.geoContext.createNode("fbxcharacterimport","Character_" + self.characterText.text())
        charNode.setParms({"fbxfile":self.charFile})
        
        restPoseNode =  self.geoContext.createNode("null","RestPose_" + self.characterText.text())
        restPoseNode.setInput(0,charNode,1)
      
        nameRemapNode = self.geoContext.createNode("MixamoNameRemap")
        nameRemapNode.setInput(0,charNode,0)
        nameRemapNode.setInput(1,charNode,1)
        nameRemapNode.setInput(2,charNode,2)

        configuratorNode = self.geoContext.createNode("MixamoApexConfigurator")
        configuratorNode.setInput(0,nameRemapNode,0)
        configuratorNode.setInput(1,nameRemapNode,1)
        configuratorNode.setInput(2,nameRemapNode,2)
        
        bipedRigNode = self.geoContext.createNode("ApexBipedRig")
        bipedRigNode.setInput(0,configuratorNode,0)
        bipedRigNode.setInput(1,configuratorNode,1)
        bipedRigNode.setInput(2,configuratorNode,2)
        
        transferAnimNode = self.geoContext.createNode("ApexTransferMixamoAnimation")
        transferAnimNode.setInput(0,bipedRigNode,0)
        transferAnimNode.setInput(1,restPoseNode)
        transferAnimNode.setInput(2,self.motionClipSubnet)
        
        sceneAnimateNode = self.geoContext.createNode("sceneanimate")
        sceneAnimateNode.setInput(0,transferAnimNode)

        sceneInvokeNode = self.geoContext.createNode("sceneinvoke")
        sceneInvokeNode.setInput(0,sceneAnimateNode)
        sceneInvokeNode.setParms({"outputpathsingle" : "/Base.char/Base.rig/output", "outputkeysingle" : "Base.shp" , "animationtarget": "/Base.char/Base.rig"})
        
        self.motionClipSubnet.setDisplayFlag(0)   
        sceneInvokeNode.setDisplayFlag(1)   
        self.geoContext.layoutChildren()
        self.close()


    def addCharacter(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter("*.fbx")
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setOptions(QFileDialog.DontUseNativeDialog)
        if dialog.exec_():
            if(len(dialog.selectedFiles()) > 0):
                self.charFile = dialog.selectedFiles()[0]
                charName = self.animationClipNameFromFile(self.charFile)
                self.characterText.insert(charName)
                
                model =  self.tableView.model()
                rowCount = model.rowCount()
                if(rowCount > 1):
                    self.apexConvertButton.setEnabled(True)
    
    def preview(self):
        model =  self.tableView.model()
        rowCount = model.rowCount()
        for count in range(rowCount):
            text = model.item(count,0).text()
            cleanedText = self.animationClipNameFromFile(text)
            model.item(count,0).setText(cleanedText)
        self.addMotionClips()
        self.previewButton.setEnabled(False)
        self.tableView.setEnabled(False)
        self.addAnimationsButton.setEnabled(False)
        
    def animationClipNameFromFile(self, fbxFile):
        fileName = os.path.basename(fbxFile)
        animName = fileName.split(".")[0]
        animName = animName.strip().replace(" ","_")
        return animName

    def addMotionClips(self):
        self.geoContext = self.objContext.createNode("geo","MixamoAnim")
        self.motionClipSubnet = self.geoContext.createNode("subnet","Animations")     
        self.motionClipSubnet.setDisplayFlag(1)   
        animNodes = []
        mClipNodes = []
        
        model =  self.tableView.model()
        rowCount = model.rowCount()

        for rCount in range(rowCount):
            animName = model.item(rCount,0).text()
            animNode = self.motionClipSubnet.createNode("fbxanimimport",animName)
            
            fbxFile = self.fbxFiles[rCount]
            animNode.setParms({"fbxfile":fbxFile})
            animNodes.append(animNode)
            
            if(rCount == 0):
                self.setLocomotionJointName(animNode)

            mClip   = self.motionClipSubnet.createNode("motionclip")
            mClip.setFirstInput(animNode)
            
            loopCount = float(model.item(rCount,1).text())
            if(loopCount >0):
                mClipCycle = self.motionClipSubnet.createNode("motionclipcycle")
                mClipCycle.setFirstInput(mClip)
                params = {"cyclesafter" : loopCount, "locomotion" : 2, "locomotionjoint": self.locomotionJointName, "matchtranslation" : 1, "orientationmethod" : 1, "method" : 1}
                mClipCycle.setParms(params)
                appendNode = mClipCycle
            else:
                appendNode = mClip
            mClipNodes.append(appendNode)
            
        lastMSequence = None
        for count in range(len(mClipNodes)):    
            if count ==0:
                lastMSequence = self.createMotionClipSequence(mClipNodes[count],mClipNodes[count+1])
            if count>1:
                lastMSequence = self.createMotionClipSequence(lastMSequence,mClipNodes[count])
        evalNode = self.motionClipSubnet.createNode("motionclipevaluate")
        evalNode.setInput(0,lastMSequence)
        outNode = self.motionClipSubnet.createNode("output","OUT_ANIM")
        outNode.setInput(0,evalNode)
        outNode.setDisplayFlag(1)
        self.motionClipSubnet.layoutChildren()


    def setLocomotionJointName(self, animNode):
        geo = animNode.geometry()
        for aPoint in geo.points():
            
            nameVal = aPoint.attribValue("name")
            nameSplit = nameVal.split(":")
            
            if(len(nameSplit) > 1):
                cleanedName = nameSplit[1]
            else:
                cleanedName = nameVal
    
            if(cleanedName.lower() == self.hipReferenceBoneName):
                self.locomotionJointName = nameVal
                break


    def createMotionClipSequence(self,input1,input2):
        newSeq = self.motionClipSubnet.createNode("motionclipsequence")
        newSeq.setInput(0,input1)
        newSeq.setInput(1,input2)
        params = {"locomotion" : 2, "locomotionjoint": self.locomotionJointName, "matchtranslation" : 1, "orientationmethod" : 1, "method" : 1}
        newSeq.setParms(params)
        return newSeq
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            indices = self.tableView.selectionModel().selectedRows() 
            for index in sorted(indices):
                self.tableView.model().removeRow(index.row()) 
            rowCount =  self.tableView.model().rowCount()
            if(rowCount > 1):
                self.previewButton.setEnabled(True)
                if(self.charFile):
                    self.apexConvertButton.setEnabled(True)
            else:
                self.previewButton.setEnabled(False)
                self.apexConvertButton.setEnabled(False)
        else:
            super().keyPressEvent(event)
        
converter = MixamoApexConverter()
converter.show()
    