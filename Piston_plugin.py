from maya.api import OpenMaya
import math
import pymel.core as pm
maya_useNewAPI = True

def check_for_intermediate_joint(joint_1_dag, joint_2_dag):
    dagModifer_1 = OpenMaya.MFnDagNode(joint_1_dag)
    dagModifer_2 = OpenMaya.MFnDagNode(joint_2_dag)
    joint_1_child = dagModifer_1.child(0)
    joint_2_parent = dagModifer_2.parent(0)
    if joint_1_child and joint_2_dag :
        if joint_1_child == joint_2_parent :
            joint_3_dag = OpenMaya.MDagPath.getAPathTo(joint_1_child)
            return joint_1_child, joint_3_dag
    else :
        OpenMaya.MGlobal.displayError('There is no intermediate child beetween {} and {}'.format(joint_1_dag.partialPathName(),
                                                                                                 joint_2_dag.partialPathName()))

def build_translate_joints(start, end) :
    print(start)
    print(end)
    start_joint = pm.PyNode(start)
    end_joint = pm.PyNode(end)
    start_pos = (pm.getAttr(start_joint.translateX),
                 pm.getAttr(start_joint.translateY),
                 pm.getAttr(start_joint.translateZ))
    end_pos = pm.xform(end_joint,q=True,t=True,ws=True)
    '''end_pos =   (pm.getAttr(end_joint.translateX)+pm.getAttr(mid_joint.translateX),
                 pm.getAttr(end_joint.translateY)+pm.getAttr(mid_joint.translateY),
                 pm.getAttr(end_joint.translateZ) + pm.getAttr(mid_joint.translateZ))'''
    print(start_pos)
    pm.select(cl = True)
    effector_start = pm.joint(name = 'TranslationStartJoint', p = start_pos)
    effectort_end = pm.joint(name= 'TranslateEndJoint', p= end_pos)
    pm.joint(effector_start, edit=True, oj = 'xyz', sao='yup')
    pm.joint(effectort_end,edit = True, o= (0, 0, 0))
    return effector_start, effectort_end

def select_joints():
    #selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.setTrackSelectionOrderEnabled(True)
    selection = OpenMaya.MGlobal.getActiveSelectionList()
    print(OpenMaya.MGlobal.trackSelectionOrderEnabled())
    if selection.length() == 2 :
        crank_rotation_joint_dag = selection.getDagPath(0)
        crank_rotation_joint_node = crank_rotation_joint_dag.node()
        shaft_end_dag = selection.getDagPath(1)
        shaft_end_node = shaft_end_dag.node()
        shaft_start_node, shaft_start_dag = check_for_intermediate_joint(crank_rotation_joint_dag,shaft_end_dag)
        return crank_rotation_joint_dag, shaft_start_dag, shaft_end_dag


    else :
        OpenMaya.MGlobal.displayError('You need to select 2 joints : {} selected'.format(selection.length()))

def build_setup() :
    rotate_center,crank_end, shaft_end = select_joints()
    effector_start, effectort_end = build_translate_joints(rotate_center, shaft_end)
    return rotate_center,crank_end, shaft_end, effector_start, effectort_end

class pistonNode(OpenMaya.MPxNode):
    ''' New solver for piston rig'''
    type_id = OpenMaya.MTypeId(0x00000001)
    type_name = 'pistonNode'
    # Attribute
    input_crank_lenght = None
    input_shaft_lenght = None
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
        cls.input_crank_lenght = numeric_attribute.create(
            'crankLenght',  # longname
            'crank_l',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_crank_lenght)

        # second attribute of the node
        cls.input_shaft_lenght = numeric_attribute.create(
            'shaftLenght',  # longname
            'shaft_R',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_shaft_lenght)

        # third attribute of the node
        cls.input_angle = numeric_attribute.create(
            'inputAngle',  # longname
            'i_angle',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = False
        numeric_attribute.writable = True
        numeric_attribute.keyable = True
        cls.addAttribute(cls.input_angle)

        # output attribute of the node
        cls.output = numeric_attribute.create(
            'output',  # longname
            'o',  # shortname
            OpenMaya.MFnNumericData.kFloat  # attribute type
        )
        numeric_attribute.readable = True
        numeric_attribute.writable = False
        cls.addAttribute(cls.output)

        # add dependencies
        cls.attributeAffects(cls.input_angle, cls.output)
        cls.attributeAffects(cls.input_shaft_lenght, cls.output)
        cls.attributeAffects(cls.input_crank_lenght, cls.output)

    def compute(self, plug, data_block):
        '''
        Compute the output of the node

        :param plug: MPlug representing the attributes to recompute
        :param data_block: MDataBlockis the storage of datas for the node's attribute
        :return:
        '''
        if plug == self.output:
            angle_value = data_block.inputValue(self.input_angle).asFloat() + 90
            shaft_lenght_value = data_block.inputValue(self.input_shaft_lenght).asFloat()
            crank_lenght_value = data_block.inputValue(self.input_crank_lenght).asFloat()

            piston_move = math.sin(math.radians(angle_value)) * crank_lenght_value + math.sqrt(
                pow(shaft_lenght_value, 2) - pow(math.cos(math.radians(angle_value )), 2) * pow(crank_lenght_value, 2))
            print(piston_move)
            # get the output handdle, set its new value and set it as clean
            output_handle = data_block.outputValue(self.output)
            output_handle.setFloat(piston_move)
            output_handle.setClean()


class generatePiston(OpenMaya.MPxCommand):
    kPluginCmdName = 'generatePistonCmd'

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    @classmethod
    def cmdCreator(cls):
        return generatePiston()

    def doIt(self, args):
        print('Done')
        rotate_center, crank_end, shaft_end, effector_start, effector_end = build_setup()
        piston_solver = pm.createNode('pistonNode')
        pm.connectAttr(rotate_center.rotateZ, piston_solver.input_angle)



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


def uninitializePlugin(plugin):
    '''
    Called when the plugin is unloaded in Maya

    :param plugin: the MObject plugin to uninitialize
    :return:
    '''

    plugin_fn = OpenMaya.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterCommand(generatePiston.kPluginCmdName)
        plugin_fn.deregisterNode(pistonNode.type_id)
    except:
        print('Failed to uninitialize the plugin :  {} !'.format(pistonNode.type_name))
        raise
