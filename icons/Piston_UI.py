import os
import pymel.core as pm
import maya.cmds as cmds


"""
This plugin is imported by Piston_plugin.py
It does generate the plugin shelf

Beware Maya crash when reloading th plugin, shelf commands change locations
and cause maya to crash. 
"""

def abspath(path):
    """
    Get the absolute path of icons images given the relative path to this file
    :param path:
    :return:
    """
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, path)
    return filename

# Shelf icons paths

icons = {
    'generatePiston': abspath('icons/generatePiston.png'),
    'deleteNodes': abspath('icons/deleteNodes.png'),
    'pistonSolverNode': abspath('icons/pistonSolverNode.png'),
    'pistonVectorLength': abspath('icons/pistonVectorLengthNode.png'),
    'flushUndo':abspath('icons/flushUndo.png')
}

# Buttons commands for the shelf

def generateCommand() :
    pm.generatePiston()


def deletePluginNodes():
    plugin_nodetypes = [
        'pistonVectorLength',
        'pistonNode'
    ]
    for type in plugin_nodetypes:
        nodes = pm.ls(type=type)
        if nodes:
            for i in range(len(nodes) - 1, -1, -1):
                if pm.objExists(nodes[i]):
                    pm.delete(nodes[i])
            print(type, ' : {} nodes deleted'.format(len(nodes)))
    pm.flushUndo()


def createSolver():
    pm.createNode('pistonNode')

def flushUndo():
    pm.flushUndo()

def createVectorLength():
    pm.createNode('pistonVectorLength')

# Generate the plugin Shelf

def generate_shelf():
    # If the shelf exists delete it
    if pm.shelfLayout('Piston plugin', exists=True):
        print('Refreshing old shelf')
        if pm.shelfLayout('Piston plugin', query=True, ca=True):
            for each in pm.shelfLayout('Piston plugin', query=True, ca=True):
                print(each)
                pm.deleteUI(each)
        pm.deleteUI('Piston_plugin')

    # Create the shelf
    plugin_shelf = pm.shelfLayout('Piston plugin', parent='ShelfLayout')

    # Create the buttons on the shelf
    pm.shelfButton(annotation='Generate a piston Rig :\n '
                              'Please, select start and end joint',
                   font='tinyBoldLabelFont',
                   command=generateCommand,
                   image=icons['generatePiston'],
                   style='iconAndTextCentered',
                   iol='AUTO',
                   parent=plugin_shelf)

    pm.shelfButton(annotation='Delete all plugin nodetypes nodes',
                   command=deletePluginNodes,
                   image=icons['deleteNodes'],
                   iol ='CLEAN',
                   parent=plugin_shelf)

    pm.shelfButton(annotation='flushUndo() command shortcut,\n'
                              'in order to avoid crash when reloading plugin',
                   command = flushUndo,
                   image=icons['flushUndo'],
                   iol='FLUSH',
                   parent=plugin_shelf)

    pm.shelfButton(annotation='Create pistonSolver in node editor',
                   command=createSolver,
                   image=icons['pistonSolverNode'],
                   parent=plugin_shelf)

    pm.shelfButton(annotation='Create a pistonVectorLength node in the node editor',
                   command=createVectorLength,
                   image=icons['pistonVectorLength'],
                   parent=plugin_shelf)

    # button that create the rig

    # button that delete all plugin-type nodes
