import math
import pymel.core as pm

from maya.api import OpenMaya
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
    build_translate_joints(rotate_center, shaft_end)

build_setup()
