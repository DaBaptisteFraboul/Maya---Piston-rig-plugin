from maya.api import OpenMaya
import math
import pymel.core as pm
maya_useNewAPI = True


def buildEffectorJoints(start, end):
    start_joint = pm.PyNode(start)
    end_joint = pm.PyNode(end)
    start_pos = (pm.getAttr(start_joint.translateX),
                 pm.getAttr(start_joint.translateY),
                 pm.getAttr(start_joint.translateZ))
    end_pos = pm.xform(end_joint, q=True, t=True, ws=True)

    pm.select(cl=True)
    effector_start = pm.joint(name='TranslationStartJoint', p=start_pos)
    effectort_end = pm.joint(name='TranslateEndJoint', p=end_pos)
    pm.joint(effector_start, edit=True, oj='xyz', sao='yup')
    pm.joint(effectort_end, edit=True, o=(0, 0, 0))

    return effector_start, effectort_end


def doPistonGraph(base_joint, crank_end_joint, shaft_end_joint, effector_end):
    axis = [
        'translateX',
        'translateY',
        'translateZ'
    ]

    angle_between_inputs = [
        '.vector1X',
        '.vector1Y',
        '.vector1Z'
    ]

    vector_inputs = [
        '.input_x',
        '.input_y',
        '.input_z'
    ]

    solver = pm.createNode('pistonNode', name='pistonSolver')
    offset_angle = pm.createNode('angleBetween', name='offsetWithCrankEnd')
    neutral_rot = pm.createNode('addDoubleLinear', name='rotateToNeutralPoint')
    shaft_length = pm.createNode('pistonVectorLength', name='shaftLength')
    crank_length = pm.createNode('pistonVectorLength', name='crankLength')
    plus_minus = pm.createNode('plusMinusAverage', name='substractOffset')

    for i in range(0, 3):
        crank_end_joint.attr(axis[i]).connect(crank_length + vector_inputs[i])
        shaft_end_joint.attr(axis[i]).connect(shaft_length + vector_inputs[i])
        crank_end_joint.attr(axis[i]).connect(offset_angle.vector1 + angle_between_inputs[i])

    base_joint.rotateZ.connect(plus_minus.input1D[0])
    offset_angle.euler.eulerZ.connect(plus_minus.input1D[1])
    # plus_minus.operation.set(2)
    plus_minus.output1D.connect(neutral_rot.input1)
    neutral_rot.input2.set(90)
    neutral_rot.output.connect(solver.inputAngle)
    shaft_length.output.connect(solver.shaftLength)
    crank_length.output.connect(solver.crankLength)
    solver.output.connect(effector_end.translateX)




def find_offset_axis(node) :
    forbiden_values = (
        90,
        -90,
        180,
        -180)
    orient_axis = ('.jointOrientX',
                   '.jointOrientY',
                   '.jointOrientZ',)
    for axis in orient_axis :
        value = pm.getAttr(node + axis)
        for forbid in forbiden_values :
            if value != (forbid or 0):
                return axis
            else :
                pass


class pistonVectorLengthNode(OpenMaya.MPxNode):
    '''A node that return the length of a given vector'''
    type_id = OpenMaya.MTypeId(0x900FF)
    type_name = 'pistonVectorLength'

    input_x = None
    input_y = None
    input_z = None
    output = None

    def __init__(self):
        OpenMaya.MPxNode.__init__(self)

    @classmethod
    def creator(cls):
        return cls()

    @classmethod
    def initialize(cls):
        print('Plugin init  : {} '.format(pistonVectorLengthNode.type_name))
        numeric_attribute = OpenMaya.MFnNumericAttribute()

        cls.input_x = numeric_attribute.create(
            'input_x',
            'x',
            OpenMaya.MFnNumericData.kFloat
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_x)

        cls.input_y = numeric_attribute.create(
            'input_y',
            'y',
            OpenMaya.MFnNumericData.kFloat
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_y)

        cls.input_z = numeric_attribute.create(
            'input_z',
            'z',
            OpenMaya.MFnNumericData.kFloat
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_z)

        cls.output = numeric_attribute.create(
            'Output',  # longname
            'output',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = True
        numeric_attribute.writable = False
        cls.addAttribute(cls.output)

        cls.attributeAffects(cls.input_x, cls.output)
        cls.attributeAffects(cls.input_y, cls.output)
        cls.attributeAffects(cls.input_z, cls.output)

    def compute(self, plug, datablock):

        if plug == self.output:
            inputX = datablock.inputValue(self.input_x).asFloat()
            inputY = datablock.inputValue(self.input_y).asFloat()
            inputZ = datablock.inputValue(self.input_z).asFloat()

            result = math.sqrt(math.pow(inputX,2) + (math.pow(inputY,2))+ (math.pow(inputZ,2)))

            output_handle = datablock.outputValue(self.output)
            output_handle.setFloat(result)
            output_handle.setClean()



class pistonNode(OpenMaya.MPxNode):
    ''' New solver for piston rig'''
    type_id = OpenMaya.MTypeId(0x00000001)
    type_name = 'pistonNode'
    # Attribute
    input_crank_length = None
    input_shaft_length = None
    input_angle = None
    output = None

    def __init__(self):
        OpenMaya.MPxNode.__init__(self)

    @classmethod
    def creator(cls):
        '''Create a node instance'''
        return cls()

    @classmethod
    def initialize(cls):
        '''Create plugin attributes with dependencies'''
        print('Plugin init  : {} '.format(pistonNode.type_name))
        # Type of attribute to create
        numeric_attribute = OpenMaya.MFnNumericAttribute()

        # first attribute of the node
        cls.input_crank_length = numeric_attribute.create(
            'crankLength',  # longname
            'crank_l',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_crank_length)

        # second attribute of the node
        cls.input_shaft_length = numeric_attribute.create(
            'shaftLength',  # longname
            'shaft_l',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_shaft_length)

        # third attribute of the node
        cls.input_angle = numeric_attribute.create(
            'inputAngle',  # longname
            'input_angle',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_angle)

        # output attribute of the node
        cls.output = numeric_attribute.create(
            'Output',  # longname
            'output',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = True
        numeric_attribute.writable = False
        cls.addAttribute(cls.output)

        # add dependencies
        cls.attributeAffects(cls.input_angle, cls.output)
        cls.attributeAffects(cls.input_shaft_length, cls.output)
        cls.attributeAffects(cls.input_crank_length, cls.output)

    def compute(self, plug, data_block):
        '''
        COpenMayapute the output of the node

        :param plug: MPlug representing the attributes to recOpenMayapute
        :param data_block: MDataBlockis the storage of datas for the node's attribute
        :return:
        '''
        if plug == self.output:
            angle_value = data_block.inputValue(self.input_angle).asFloat() + 90
            shaft_length_value = data_block.inputValue(self.input_shaft_length).asFloat()
            crank_length_value = data_block.inputValue(self.input_crank_length).asFloat()

            piston_move = math.sin(math.radians(angle_value)) * crank_length_value + math.sqrt(
                pow(shaft_length_value, 2) - pow(math.cos(math.radians(angle_value )), 2) * pow(crank_length_value, 2))

            # get the output handdle, set its new value and set it as clean
            output_handle = data_block.outputValue(self.output)
            output_handle.setFloat(piston_move)
            output_handle.setClean()


class generatePiston(OpenMaya.MPxCommand):
    kPluginCmdName = 'generatePiston'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @classmethod
    def cmdCreator(cls):
        return generatePiston()

    def doIt(self, args):

        # get selection
        selection = pm.ls(selection=True, type='joint')

        # test if selected is a joint and that it has only 2 children that are also joints
        if selection:
            print(pm.nodeType(selection[0]))
            if len(selection) == 2 and pm.nodeType(selection[0]) == 'joint':
                base_joint = selection[0]
                direct_child = pm.listRelatives(base_joint, type='joint')
                base_joint.setAttr('displayLocalAxis', True)
                if len(direct_child) == 1:
                    base_joint.rotateX.unlock()
                    base_joint.rotateY.unlock()
                    shaft_end = selection[1]
                    print('shaft_end joint = {}'.format(shaft_end))
                    crank_end = direct_child[0]
                    print('crank_end joint = {}'.format(crank_end))

                    pm.parent((base_joint, shaft_end, crank_end), world=True)
                    # do the aim constraint to properly align basejoint to children
                    temp_constraint = pm.aimConstraint(shaft_end, base_joint, worldUpType='object',
                                                       worldUpObject=crank_end)
                    pm.refresh()
                    pm.delete(temp_constraint)

                    effector_start, effector_end = buildEffectorJoints(base_joint, shaft_end)
                    pm.delete(shaft_end)
                    pm.select(clear=True)
                    start_pos = pm.xform(effector_end, q=True, t=True, ws=True)
                    end_pos = pm.xform(crank_end, q=True, t=True, ws=True)
                    shaft_start = pm.joint(name='shaft_start_joint', p=end_pos)
                    shaft_end = pm.joint(name='shaft_end_joint', p=start_pos)

                    pm.aimConstraint(crank_end, shaft_end)
                    pm.parent(shaft_end, effector_end)
                    pm.parent(shaft_start, shaft_end)
                    root_joint = pm.duplicate(base_joint, name='Root_joint')[0]
                    root_joint.radius.set(2 * base_joint.radius.get())
                    pm.parent(effector_start, root_joint)
                    pm.parent(base_joint, root_joint)
                    pm.makeIdentity(base_joint, apply=True)
                    pm.parent(crank_end, base_joint)
                    doPistonGraph(base_joint, crank_end, shaft_start, effector_end)
                    base_joint.rotateX.lock()
                    base_joint.rotateY.lock()

                else:
                    OpenMaya.MGlobal.displayError('First joint must have only children to generate piston rig')
            else:
                OpenMaya.MGlobal.displayError('You must select only 2 joint : start and end joints')

        # no selection
        else:
            OpenMaya.MGlobal.displayError('Empty selection')


def initializePlugin(plugin):
    '''
    Called when the plugin is initialized

    :param Plugin: MObject the plugin to initialize
    :return:
    '''

    plugin_fn = OpenMaya.MFnPlugin(plugin, 'Baptiste Fraboul', '0.0.1')

    try:
        plugin_fn.registerCommand(generatePiston.kPluginCmdName,
                                  generatePiston.cmdCreator)
    except :
        OpenMaya.MGlobal.displayError('Failed to initialize command : {}'.format(generatePiston.kPluginCmdName))
        raise

    try :
        plugin_fn.registerNode(
            pistonNode.type_name,
            pistonNode.type_id,
            pistonNode.creator,
            pistonNode.initialize,
            OpenMaya.MPxNode.kDependNode
        )
    except:
        print('Failed to initialize the plugin :  {} !'.format(pistonNode.type_name))
        raise
    try :
        plugin_fn.registerNode(
            pistonVectorLengthNode.type_name,
            pistonVectorLengthNode.type_id,
            pistonVectorLengthNode.creator,
            pistonVectorLengthNode.initialize,
            OpenMaya.MPxNode.kDependNode
        )
    except :
        print('Failed to initialize the plugin :  {} !'.format(pistonVectorLengthNode.type_name))
        raise
def uninitializePlugin(plugin):
    '''
    Called when the plugin is unloaded in Maya

    :param plugin: the MObject plugin to uninitialize
    :return:
    '''

    plugin_fn = OpenMaya.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterCommand(generatePiston.kPluginCmdName)
        plugin_fn.deregisterNode(pistonVectorLengthNode.type_id)
        plugin_fn.deregisterNode(pistonNode.type_id)
    except:
        print('Failed to uninitialize the plugin :  {} !'.format(pistonNode.type_name))
        raise
