import bpy
from bpy.props import BoolProperty
import mathutils
import math
import random
from mathutils import Matrix, Euler

bl_info = {
    "name": "Linked Collection Toolbox",
    "blender": (2, 80, 0),
    "category": "Object",
}

'''
LINKED COLLECTION TOOLBOX
    A Blender Addon to manage Linked Collections
    by Markus Koepke (https://github.com/theghostronaut)

    Tool 1: CREATE LINKED COLLECTION
        - Creates a linked collection from the selected object's collection
        - Adds the (Linked) suffix to the name of the new collection and (Original) to the name of the original collection
        - Color codes both collections
        - Moves the linked collections into a parent collection from better organization
        - Automatically selects all objects in the newly created linked collection
        - Sets the new collection to be the active scene collection

    Tool 2: SYNC OBJECT
        - Looks for linked collections based on the currently selected object
        - Checks if any of the linked collections are missing the object from the current collection
        - Copies the missing object or all missing objects over to all linked collections, matching its respective location (scale and rotation are curently not matched due to cluelessness)

    Tool 3: REMOVE OBJECT
        - Looks for linked collections based on the currently selected object
        - Removes the currently selected object from all linked collections (but keeps it in the current collection)

    Tool 4: HELPERS
        - Select all objects in collection
        - Set active collection based on selected object


    KNOWN ISSUES:
    - When all objects from the linked collection have been removed, the sync doesn't work anymore (there are no reference objects).
    This could probably be fixed by checking for empty collections with the (Linked) suffix in the Link Group. TBD.

'''

bpy.types.Scene.unhide_objects = BoolProperty(
    name="Unhide Objects",
        description="After creating a linked collection, any objects that were hidden from the viewport will be made visible again, so they can be moved with the selection",
        default = False)

#########################################

# TOOL 1: CREATE LINKED COLLECTION

# Helper function to get Collection from CollectionLayer, found here: https://blender.stackexchange.com/a/127700 
def recur_layer_collection(layer_coll, coll_name):
    if layer_coll.name == coll_name:
        return layer_coll
    for layer in layer_coll.children:
        found = recur_layer_collection(layer, coll_name)
        if found:
            return found
        
# Helper function to check if a collection has a parent collection with a specific string in its name
def is_collection_within_parent_with_string(collection, parent_collection_name_contains):
    parent_collection = None
    parent_collection_is_link_group = False
    for col in bpy.data.collections:
        if col.children.get(collection.name):
            if parent_collection_name_contains in col.name:
                parent_collection = col
                parent_collection_is_link_group = True
                break
            else:
                parent_collection = col
                break
    return (parent_collection, parent_collection_is_link_group)


class CreateLinkedCollectionOperator(bpy.types.Operator):
    bl_idname = "object.create_linked_collection_operator"
    bl_label = "Create Linked Collection"
    bl_description = "Create a Linked Collection from the currently selected object's collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        link_group_name_suffix = "(Link Group)"
        linked_collection_name_suffix = "(Linked)"
        original_collection_name_suffix = "(Original)"
        original_collection_color_tag = 'COLOR_02'
        linked_collection_color_tag = 'COLOR_03'
        link_group_collection_color_tag = 'COLOR_04'

        # what collection is the active scene collection?
        #selected_collection = bpy.context.view_layer.active_layer_collection.collection

        # if the amount of selected objects is < 1, set active_object to be the first object in the active scene collection
        if len(context.selected_objects) == 0:
            active_object = bpy.context.view_layer.active_layer_collection.collection.objects[0]
        else:
            active_object = context.active_object

        selected_collection = active_object.users_collection[0]
        # if the selected_collection is the scene collection, create a new collection and move the selected object into it
        if selected_collection == bpy.context.scene.collection:
            # Create a new collection with the name of the selected object
            new_collection = bpy.data.collections.new(active_object.name)
            # Link the new collection to the scene collection
            bpy.context.scene.collection.children.link(new_collection)
            # Set the new collection to be the active scene collection
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[active_object.name]
            # Move the selected object into the new collection
            new_collection.objects.link(active_object)
            selected_collection = new_collection

        # Get the name of the selected collection
        selected_collection_name = selected_collection.name

        if active_object:
            # Handle the naming of the new collection
            # Rename the new collection and the original collection
            # If the collection is an original collection, add the "(Linked)" suffix to the new collection's name and omit "Original"
            if (original_collection_name_suffix in selected_collection_name):
                new_collection_name = selected_collection_name.replace(original_collection_name_suffix, linked_collection_name_suffix)
            # If the collection is a linked collection, just use the selected collection's name plus a number
            elif (linked_collection_name_suffix in selected_collection_name):
                new_collection_name = selected_collection_name
            # If the collection is neither an original collection nor a linked collection, add the "(Linked)" suffix to the new collection's name and "Original" to the selected collection's name
            else:
                new_collection_name = f"{selected_collection_name} {linked_collection_name_suffix}"
                selected_collection.name = f"{selected_collection_name} {original_collection_name_suffix}"
                selected_collection.color_tag = original_collection_color_tag
            
            # Create the new collection with the defined name
            new_collection = bpy.data.collections.new(new_collection_name)

            # Check if the collection is within another collection
            parent_collection, parent_collection_is_link_group = is_collection_within_parent_with_string(selected_collection, link_group_name_suffix)
            # If so, set the new collection to be within the same parent collection as the original collection
            if (parent_collection_is_link_group):
                # Set the new collection to be within the same parent collection as the original collection
                parent_collection.children.link(new_collection)
            # otherwise, create a new parent collection and set the new collection and the original collection to be within it
            else:
                # Create a new parent collection
                new_parent_collection = bpy.data.collections.new(f"{selected_collection_name} {link_group_name_suffix}")
                # link the new_parent_collection to parent_collection to preserve the hierarchy if the original collection is within a parent collection
                if (parent_collection):
                    parent_collection.children.link(new_parent_collection)
                    parent_collection.children.unlink(selected_collection)
                else:
                    bpy.context.scene.collection.children.link(new_parent_collection)
                    bpy.context.scene.collection.children.unlink(selected_collection)

                # Set the original collection to be within the new parent collection
                new_parent_collection.children.link(selected_collection)
                # Set the new collection to be within the new parent collection
                new_parent_collection.children.link(new_collection)
                # Set color tags for the new parent collection
                new_parent_collection.color_tag = link_group_collection_color_tag
                
            # Set color tags for the new collection
            new_collection.color_tag = linked_collection_color_tag
            
            # Copy all objects from the original collection to the new collection
            for obj in selected_collection.objects:
                new_obj = obj.copy()
                new_collection.objects.link(new_obj)

            # Set the newly created collection to be the active scene collection for convenience
            ucol = active_object.users_collection
            layer_collection = bpy.context.view_layer.layer_collection
            for collection in ucol:
                layer_coll = recur_layer_collection(layer_collection, new_collection.name)
                if layer_coll:
                    bpy.context.view_layer.active_layer_collection = layer_coll
                    break
            
            # Select objects in the new collection and deselect objects in the original collection, for convenience
            # Also make any object hidden from the viewport visible again, so they will be moved with the selection, if the option is set in the Toolbox

            # if unhide_objects from the scene is set to True, make all hidden objects visible
            if (bpy.context.scene.unhide_objects):
                # make all objects in the new collection visible
                for obj in new_collection.objects:
                    obj.hide_viewport = False                   
            
            bpy.ops.object.select_all(action='DESELECT')
            for obj in new_collection.objects:
                obj.select_set(True)
            
            # Select one of the objects in the new collection to be the active object
            bpy.context.view_layer.objects.active = new_collection.objects[0]

            return {'FINISHED'}
        else:
            return {'CANCELLED'}

# TOOL 2: SYNC OBJECTS

def display_message(message, type='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=f"{type.capitalize()} Message", icon=type)


class SyncObjectsOperator(bpy.types.Operator):
    bl_idname = "object.sync_objects_operator"
    bl_label = "Sync Objects"
    bl_description = "Sync active object to linked collections\n- Select another object as reference to match position, scale & rotation\n- Select any object from any linked collections to sync only to those collections"
    bl_options = {'REGISTER', 'UNDO'}

    sync_all_objects: bpy.props.BoolProperty(name="Sync All Objects", default=False)
    add_to_missing: bpy.props.BoolProperty(name="Add to missing", default=False)

    def handle_sync(self, context, active_object, linked_collection, linked_objects, reference_obj, ref_obj_selected):
        
        new_obj = active_object.copy()
        linked_collection.objects.link(new_obj)

        # a specific reference object was not selected, so use the original reference object
        if not ref_obj_selected:
            linked_reference_obj = next((linked_obj for linked_obj in linked_objects if linked_obj.data == reference_obj.data), None)
            offset_selected_to_linked = linked_reference_obj.location - reference_obj.location
            new_obj.location += offset_selected_to_linked
        # perform specific transformation actions based on the selected reference object
        else:
            # find the object in the linked collection that is equal to selected_ref_obj based on object data
            linked_ref_obj = next((linked_obj for linked_obj in linked_objects if linked_obj.data == ref_obj_selected.data), None)
            
            # check if linked_ref_obj was found
            if linked_ref_obj:

                ###### MATCH SCALE ######

                # copy the scale of linked_ref_obj for later use
                previous_scale_linked_ref_obj = linked_ref_obj.scale.copy()
                previous_location_linked_ref_obj = linked_ref_obj.location.copy()

                # save the matrix world of linked_ref_obj for later use
                previous_matrix_world_linked_ref_obj = linked_ref_obj.matrix_world.copy()

                # check the difference in scale between ref_obj_selected and linked_ref_obj
                offset_scale_selected_to_linked = linked_ref_obj.scale - ref_obj_selected.scale

                # get tbe scaling factor, assuming uniform scaling
                #scale_factor = linked_ref_obj.scale.x / ref_obj_selected.scale.x

                # get the scaling factor for each axis
                scale_factor_x = linked_ref_obj.scale.x / ref_obj_selected.scale.x
                scale_factor_y = linked_ref_obj.scale.y / ref_obj_selected.scale.y
                scale_factor_z = linked_ref_obj.scale.z / ref_obj_selected.scale.z
                
                # Match the scale of linked_ref_obj to ref_obj_selected
                linked_ref_obj.scale = ref_obj_selected.scale

                ###### MATCH LOCATION & ROTATION ######

                # check the difference in location between ref_obj_selected and linked_ref_obj
                offset_location_selected_to_linked = linked_ref_obj.location - ref_obj_selected.location
                
                # Calculate the rotation difference matrix between linked_ref_obj and ref_obj_selected for later use
                rotation_difference_matrix = linked_ref_obj.rotation_euler.to_matrix() @ ref_obj_selected.rotation_euler.to_matrix().inverted()
                # Match the rotation of linked_ref_obj to ref_obj_selected so new_obj can be correctly positioned and be rotated with linked_ref_obj later
                linked_ref_obj.rotation_euler = ref_obj_selected.rotation_euler

                # Position new_obj with the offset_location_selected_to_linked
                new_obj.location += offset_location_selected_to_linked

                # Handle rotation using context:
                # Set linked_ref_obj to be the active obj
                bpy.context.view_layer.objects.active = linked_ref_obj

                # Convert rotation matrix to Euler angles
                rotation_difference_euler = rotation_difference_matrix.to_euler('XYZ')

                # Set the pivot point for rotation to be the origin of linked_ref_obj
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

                # Get the pivot location
                pivot_location = linked_ref_obj.location

                # Calculate the rotation matrix for each axis
                rotation_matrix = Euler(rotation_difference_euler, 'XYZ').to_matrix()

                # Calculate the scaling matrix for each axis
                scaling_matrix = Matrix.Diagonal((scale_factor_x, scale_factor_y, scale_factor_z)).to_4x4()

                # Calculate the rotation angles for each axis
                rotation_angle_x, rotation_angle_y, rotation_angle_z = rotation_difference_matrix.to_euler('XYZ')

                # Calculate the scaling matrix
                scaling_matrix = Matrix.Scale(scale_factor_x, 4)

                # Calculate the transformation matrix for rotation around the pivot
                rotation_matrix = Euler(rotation_difference_euler).to_matrix().to_4x4()

                # Calculate the transformation matrix for scaling around the pivot
                scaling_matrix = Matrix.Diagonal((scale_factor_x, scale_factor_y, scale_factor_z)).to_4x4()

                # Calculate the transformation matrix for translation to the pivot point
                translation_to_pivot_matrix = Matrix.Translation(-pivot_location)

                # Calculate the transformation matrix for translation back from the pivot point
                translation_from_pivot_matrix = Matrix.Translation(pivot_location)

                # Combine the matrices in the correct order for the transformation
                transformation_matrix = translation_from_pivot_matrix @ scaling_matrix @ rotation_matrix @ translation_to_pivot_matrix

                # Apply the transformation matrix to both linked_ref_obj and new_obj
                for obj in [linked_ref_obj, new_obj]:
                    obj.matrix_world = transformation_matrix @ obj.matrix_world

                # Deselect all objects
                bpy.ops.object.select_all(action='DESELECT')
            else:
                # If linked_obj does not exist (assuming it was deleted or never existed), let's give the user an error message for now. Maybe we can do something more useful later.
                display_message("Reference object not found in linked collection, please select an existing reference object", type='ERROR')
                # remove new_obj   
                bpy.data.objects.remove(new_obj, do_unlink=True)
                return {'CANCELLED'}
        
            #linked_ref_obj.location = previous_location_linked_ref_obj
            # apply the previous matrix world of linked_ref_obj
            #linked_ref_obj.matrix_world = previous_matrix_world_linked_ref_obj


            
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}
    



    def execute(self, context):
       
        # get all selected objects and save their matrix world in a list
        pre_origin_fix_selected_objects = []
        for selected_obj in bpy.context.selected_objects:
            selected_obj_previous_location = selected_obj.location.copy()
            pre_origin_fix_selected_objects.append((selected_obj, selected_obj_previous_location))

        SetOrigin.set_origin_to_geometry(self, context) ## Find a way to make this more efficient. Check if the origin is already at ORIGIN_GEOMETRY before setting it there.

        # loop through pre_origin_fix_selected_objects and apply the previous matrix world to each object
        #for selected_obj, selected_obj_previous_location in pre_origin_fix_selected_objects:
            #selected_obj.location = selected_obj_previous_location

        # Get the currently active object
        active_object = context.active_object

        _sync_to_linked_collection = None
        _reference_obj = None

        if active_object:
            # A reference object is selected
            if len(context.selected_objects) == 3:
                # The object that is not the active object and is in the same collection as the active object is the reference object
                _reference_obj = next((obj for obj in context.selected_objects if obj != active_object and obj.users_collection[0] == active_object.users_collection[0]), None)
                # Get the index of _reference_obj in the list of selected objects
                if _reference_obj:
                    _reference_obj_index = context.selected_objects.index(_reference_obj)
                    # Get the index of the object in the list of selected objects that is not the active object and not the reference object
                    _other_selected_obj_index = next((index for index in range(len(context.selected_objects)) if index != _reference_obj_index and index != context.selected_objects.index(active_object)), None)
                    # The object with the index _other_selected_obj_index is the object that is not the active object and not the reference object
                    # This is the object from the other linked collection that we want to sync to
                    _sync_to_linked_obj = context.selected_objects[_other_selected_obj_index]
                    # Get the collection of _ref_linked
                    _sync_to_linked_collection = _sync_to_linked_obj.users_collection[0]
    
            # 3 objects are selected
            if len(context.selected_objects) > 3:
                display_message("Please only select 3 objects: - 1 to sync the object to all linked collections\n- 2 to sync the active to all linked collections, matching relative position, scale, rotation to the second selected object\n- 2+1 from another linked collection to only sync to that collection.", type='ERROR')
                return {'CANCELLED'}
            
            linked_collections = []
            # Get the collection belonging to the selected object
            selected_collection = active_object.users_collection[0]

            # Check if _sync_to_linked_collection is a linked collection to any of the selected objects by comparing object data of the selected objects to the objects in the collection
            if _sync_to_linked_collection:
                if any(linked_obj.data == selected_obj.data for linked_obj in _sync_to_linked_collection.objects for selected_obj in context.selected_objects):
                    linked_collections.append(_sync_to_linked_collection)
            else:
                # Check if any linked collections related to this collection exist
                for collection in bpy.data.collections:
                    if any(linked_obj.data == selected_obj.data for linked_obj in collection.objects for selected_obj in selected_collection.objects if selected_obj.original):
                        linked_collections.append(collection)

            ### DO SOME CLEAN UP FROM HERE ON ###

            # Get reference object from the linked collection ## Should rename this, its super confusing
            reference_obj = None
            for obj in selected_collection.objects:
                if obj.original:
                    missing_in_linked_collections = []
                    for linked_collection in linked_collections:
                        linked_objects = set(linked_collection.objects)
                        found_in_linked_collections = any(linked_obj.data == obj.data and linked_obj != active_object for linked_obj in linked_objects)
                        if not found_in_linked_collections:
                            missing_in_linked_collections.append(linked_collection.name)
                    if not missing_in_linked_collections:
                        reference_obj = obj
                        break

            if reference_obj:

                # If sync_all_objects is True, copy missing objects to linked collections
                if self.sync_all_objects:
                    missing_objects = []
                    for obj in selected_collection.objects:
                        if obj.original:
                            missing_in_linked_collections = []
                            for linked_collection in linked_collections:
                                linked_objects = set(linked_collection.objects)
                                found_in_linked_collections = any(linked_obj.data == obj.data for linked_obj in linked_objects)
                                if not found_in_linked_collections:
                                    missing_in_linked_collections.append(linked_collection.name)
                                    new_obj = obj.copy()
                                    linked_reference_obj = next((linked_obj for linked_obj in linked_objects if linked_obj.data == reference_obj.data), None)

                                    if linked_reference_obj:
                                        offset_selected_to_linked = linked_reference_obj.location - reference_obj.location
                                        new_obj.location += offset_selected_to_linked

                                    linked_collection.objects.link(new_obj)
                            missing_objects.append((obj.name, missing_in_linked_collections))
                else:
                    # If sync_all_objects is False, copy only the selected object to linked collections
                    missing_in_linked_collections = []
                    ref_obj_selected = None

                    # set a specific reference object if one was selected, for performing specific transformation actions later
                    if _reference_obj:
                        ref_obj_selected = _reference_obj
                    else:
                        if len(context.selected_objects) > 1:
                            for obj in context.selected_objects:
                                if obj != active_object:
                                    ref_obj_selected = obj
                                    break
                    
                    # check if the active object was found in any of the linked collections
                    for linked_collection in linked_collections:
                        linked_objects = set(linked_collection.objects)
                        found_in_linked_collections = any(linked_obj.data == active_object.data for linked_obj in linked_objects)
                        # get linked_obj data from linked_collections
                        
                        if not found_in_linked_collections:
                            missing_in_linked_collections.append(linked_collection.name)
                            
                            self.handle_sync(context, active_object, linked_collection, linked_objects, reference_obj, ref_obj_selected)
                                
                        else:
                            linked_object = next((linked_obj for linked_obj in linked_objects if linked_obj.data == active_object.data), None)
                            
                            if ref_obj_selected:
                                found_ref_obj_in_linked_collections = any(linked_obj.data == ref_obj_selected.data for linked_obj in linked_objects)
                                
                                if found_ref_obj_in_linked_collections:
                                    self.handle_sync(context, active_object, linked_collection, linked_objects, reference_obj, ref_obj_selected)
                                    linked_collection.objects.unlink(linked_object)
                                else:
                                    active_object, ref_obj_selected = ref_obj_selected, active_object
                                    missing_in_linked_collections.append(linked_collection.name)
                                    self.handle_sync(context, active_object, linked_collection, linked_objects, reference_obj, ref_obj_selected)
                            else:
                                    self.handle_sync(context, active_object, linked_collection, linked_objects, reference_obj, ref_obj_selected)
                                    linked_collection.objects.unlink(linked_object)

                            
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        '''
        

        # Select other_selected_obj
        if other_selected_obj:
            other_selected_obj.select_set(True)
        # Select active_object and make it active
        if active_object:
            active_object.select_set(True)
            bpy.context.view_layer.objects.active = active_object
        '''

        return {'FINISHED'}

#########################################    
# Tool 3: REMOVE OBJECTS
# update this code to have a Remove selected object and remove all objcets button


class RemoveSelectedObjectOperator(bpy.types.Operator):
    bl_idname = "object.remove_selected_object_operator"
    bl_label = "Remove Selected from Linked Collections"
    bl_description = "Remove the active object from all linked Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the currently selected object
        active_object = context.active_object
    
        if active_object:
            # Get the collection belonging to the selected object
            selected_collection = active_object.users_collection[0]

            # Check if any linked collections related to this collection exist
            
            linked_collections = []
            for collection in bpy.data.collections:
                if any(linked_obj.data == selected_obj.data for linked_obj in collection.objects for selected_obj in selected_collection.objects if selected_obj.original):
                    # exclude the selected object's collection from the list of linked collections
                    if collection != selected_collection:
                        linked_collections.append(collection)
            # check if the selected object is inside any of the linked collections based on object data, if so, remove it
            for linked_collection in linked_collections:
                linked_objects = set(linked_collection.objects)
                # loop through the linked collections and find the object based on object data, and return it as an object
                linked_object = next((linked_obj for linked_obj in linked_objects if linked_obj.data == active_object.data), None)
                # if the object is found, remove it from the linked collection
                if linked_object:
                    linked_collection.objects.unlink(linked_object)
                else:
                    display_message("Object not found in any linked collections", type='INFO')

       

        return {'FINISHED'}
 

#########################################
# Tool 4: Helpers

# Tool for selecting all objects in collection
class SelectAllObjectsInCollection(bpy.types.Operator):
    bl_idname = "object.select_all_objects_in_collection_operator"
    bl_label = "Select all in Collection"
    bl_description = "Select all objects belonging to the same collection as the currently selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the currently selected object
        active_object = context.active_object

        if active_object:
            # Get the collection belonging to the selected object
            selected_collection = active_object.users_collection[0]

            # Select all objects in the collection and add them to the selection even the ones hidden from the viewport (make the temporarily visible)
            #bpy.ops.object.select_all(action='DESELECT')
            for obj in selected_collection.objects:
                obj.select_set(True)
            

        return {'FINISHED'}
    
###

# Tool for setting the active collection based on the selected object
class SetActiveCollectionBasedOnSelectedObject(bpy.types.Operator):
    bl_idname = "object.set_active_collection_operator"
    bl_label = "Set Active Collection"
    bl_description = "Set the active Collection based on the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the currently selected object
        active_object = context.active_object

        if active_object:
            # Get the collection belonging to the selected object
            selected_collection = active_object.users_collection[0]

            # Set the collection to be the active scene collection
            ucol = active_object.users_collection
            layer_collection = bpy.context.view_layer.layer_collection
            for collection in ucol:
                layer_coll = recur_layer_collection(layer_collection, selected_collection.name)
                if layer_coll:
                    bpy.context.view_layer.active_layer_collection = layer_coll
                    break

        return {'FINISHED'}
    
####

# Tool for setting the origin of a selected object to its geometry and keeping the location of any linked objects intact
class SetOrigin(bpy.types.Operator):
    bl_idname = "object.set_origin_operator"
    bl_label = "Set Origin to Geometry"
    bl_description = "Set the origin of all selected objects (and any linked objects) to their geometry while retaining the location of any linked objects"
    bl_options = {'REGISTER', 'UNDO'}

    def set_origin_to_geometry(self, context):
        # Get the currently active object
        active_object = context.active_object

        # Just in case, set the origin of each selected object to their respective geometry (otherwise wrong calculations will happen later)
        # If the origin was not already at ORIGIN_GEOMETRY, this will most likely change the positon of linked objects. We need to change them back to their previous location.
        # Haven't found a way to make this more efficient yet.
        
        # Save all selected objects in a list
        selected_objects = []
        for selected_obj in bpy.context.selected_objects:
            selected_objects.append(selected_obj)
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        linked_objects_init = []
        # Loop through the selected objects list
        for selected_obj in selected_objects:
            # Loop through all the objects in the scene that have matching data to the selected object (=linked objects)
            for linked_obj in bpy.context.scene.objects:
                if linked_obj.data == selected_obj.data and linked_obj != selected_obj:
                    linked_obj_duplicate_location = None
                    ## hacky fix for floating point errors when changing the origin
                    # make a duplicate of linked_obj
                    linked_obj_duplicate = linked_obj.copy()

                    # make linked_obj_duplicate independent from linked_obj
                    linked_obj_duplicate.data = linked_obj.data.copy()

                    # link to the scene
                    bpy.context.scene.collection.objects.link(linked_obj_duplicate)

                    # select the duplicate
                    bpy.ops.object.select_all(action='DESELECT')
                    linked_obj_duplicate.select_set(True)               

                    # set the origin of the duplicate to its geometry
                    bpy.context.view_layer.objects.active = linked_obj_duplicate
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                    # save the location of the duplicate
                    linked_obj_duplicate_location = linked_obj_duplicate.location.copy()
                    
                    # unselct the duplicate
                    linked_obj_duplicate.select_set(False)

                    # delete the duplicate
                    bpy.data.objects.remove(linked_obj_duplicate, do_unlink=True)

                    # save linked_obj and its location data
                    linked_objects_init.append((linked_obj, linked_obj_duplicate_location))

                    '''
                    # Get the centroid (center of mesh) for the linked_obj:
                    # Make the linked_obj the active object
                    bpy.context.view_layer.objects.active = linked_obj
                    # Enter Edit Mode to work with vertices
                    bpy.ops.object.mode_set(mode='EDIT')
                    # Select all vertices
                    bpy.ops.mesh.select_all(action='SELECT')
                    # Snap the cursor to the center of the selected vertices
                    bpy.ops.view3d.snap_cursor_to_selected()

                    # save the centroid location
                    centroid_location = bpy.context.scene.cursor.location.copy()
                    # print name and centroid location of linked_obj
                    print(f"{linked_obj.name} centroid location: {centroid_location}")

                    # save linked_obj and its centroid location
                    linked_objects_init.append((linked_obj, centroid_location, linked_obj_duplicate_location))
                    
                    # Exit Edit Mode
                    bpy.ops.object.mode_set(mode='OBJECT')

                    # Deselect linked_obj and make it not active
                    linked_obj.select_set(False)

                    '''
            
        # Select active_object and make it active
        if active_object:
            active_object.select_set(True)
            bpy.context.view_layer.objects.active = active_object

        # Select all objects in selected_objects
        for selected_obj in selected_objects:
            selected_obj.select_set(True)

        # Set the origin of each selected object to its geometry
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        # Set the location of each linked object to its previous location
        for linked_obj, linked_obj_duplicate_location in linked_objects_init:

            linked_obj.location = linked_obj_duplicate_location

            # Translate the matrix of linked_obj to centroid location
            #linked_obj.matrix_world.translation = centroid_location


        return {'FINISHED'}

    def execute(self, context):
        self.set_origin_to_geometry(context)

        return {'FINISHED'}

# Tool for disabling all selected objects in the viewport
class DisableSelectedInViewport(bpy.types.Operator):
    bl_idname = "object.disable_selected_in_viewport_operator"
    bl_label = "Disable Selected in Viewport"
    bl_description = "Disables the selected objects in the Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the currently selected objects
        selected_objects = context.selected_objects
        # Disable them in the viewport
        for obj in selected_objects:
            obj.hide_viewport = True


        return {'FINISHED'}
    
####

#########################################
# TOOLBOX PANEL + REGISTRATION

class LinkedCollectionToolBoxPanel(bpy.types.Panel):
    bl_label = "Linked Collection Toolbox"
    bl_idname = "OBJECT_PT_create_linked_collection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LC Toolbox'

    # checkbox property for the option to move hidden objects with the selection
    show_hidden_objects: bpy.props.BoolProperty(name="Show hidden objects", default=False)

    def draw(self, context):
        layout = self.layout

        # Tool 1: Create Linked Collection
        layout.label(text="LINKED COLLECTION")
        # add a checkbox for the option to move hidden objects with the selection
        layout.prop(context.scene, "unhide_objects", text="Unhide hidden objects")
        layout.operator("object.create_linked_collection_operator",text="Create Linked Collection",icon="LINKED")
        layout.separator()

        # Tool 2: Sync Objects
        layout.label(text="SYNC OBJECTS")
        layout.operator("object.sync_objects_operator",text="Sync Active",icon="UV_SYNC_SELECT")
        #layout.operator("object.sync_objects_operator", text="Add to missing").add_to_missing = True
        #layout.operator("object.sync_objects_operator", text="Sync All Objects").sync_all_objects = True
        layout.separator()
        
        # Tool 3: Remove Objects
        layout.label(text="REMOVE OBJECTS")
        layout.operator("object.remove_selected_object_operator",text="Remove Active",icon="TRASH")
        layout.separator()
        
        # Tool 4: Helpers
        layout.label(text="HELPERS")
        # Tool for selecting all objects in collections
        layout.operator("object.select_all_objects_in_collection_operator",text="Select all in Collection",icon="SELECT_EXTEND")
                        
        # Tool for setting the active collection based on the selected object
        layout.operator("object.set_active_collection_operator",text="Set active Collection",icon="GROUP")

        # Tool for setting the origin of a selected object to its geometry and keeping the location of any linked objects intact
        layout.operator("object.set_origin_operator",text="Set Origin to Geometry",icon="PIVOT_ACTIVE")

        # Tool for disabling all selected objects in the viewport
        layout.operator("object.disable_selected_in_viewport_operator",text="Disable selected in Viewport",icon="HIDE_ON")

def register():
    bpy.utils.register_class(CreateLinkedCollectionOperator)
    bpy.utils.register_class(SyncObjectsOperator)
    bpy.utils.register_class(RemoveSelectedObjectOperator)
    bpy.utils.register_class(SetActiveCollectionBasedOnSelectedObject)
    bpy.utils.register_class(SelectAllObjectsInCollection)
    bpy.utils.register_class(LinkedCollectionToolBoxPanel)
    bpy.utils.register_class(SetOrigin)
    bpy.utils.register_class(DisableSelectedInViewport)

def unregister():
    bpy.utils.unregister_class(CreateLinkedCollectionOperator)
    bpy.utils.unregister_class(SyncObjectsOperator)
    bpy.utils.unregister_class(RemoveSelectedObjectOperator)
    bpy.utils.unregister_class(SetActiveCollectionBasedOnSelectedObject)
    bpy.utils.unregister_class(SelectAllObjectsInCollection)
    bpy.utils.unregister_class(LinkedCollectionToolBoxPanel)
    bpy.utils.unregister_class(DisableSelectedInViewport)
    bpy.utils.unregister_class(SetOrigin)

if __name__ == "__main__":
    register()

# end of linked_collection_toolbox.py
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
########################