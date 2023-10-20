# LinkedCollectionToolbox
A Blender plugin for better linked collections (Compatibility checked with 3.6.1)

https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/24f7a0ac-99cd-4e61-bdca-2418bf6c8390

## Installation
Download linked_collection_toolbox.py, add it to Blender Addons (Edit > Preferences > Add-ons > "Install") and activate it.
A new tab "Linked Collection Toolbox" will be added to the Viewport toolbar (N)

## Disclaimer
I originally intended to sell this add-on but since I'm currently not finding the time to add some functionality that would make sense to be included, plus I would need to refactor the code (it's pretty messy), I decided to release it for free. Bare in mind that the plugin won't really give you any hints when something goes wrong and it might be buggy. But in my testing at least, as long as you do basic stuff as described below, everything should work.

## Tool 1: Create Linked Collection
Creates a linked collection from the currently active object, organising and naming it and selecting all the objects in the new collection

![1](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/639629b1-34bf-4c55-9b9a-ac4a74d644d1)

Changes made to objects in Edit mode will by synced to all linked collections, as usual.

![2](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/989f31f4-a7ff-486b-b144-a7f3d66755c8)

There is one thing to be aware of: Blender doesn't actually link the collection but rather only the objects. My add-on handles all of that internally.
But the issue here is that objects that are set to be hidden from the viewport (not those hidden with the Eye icon but hidden via Object>Visibility!) will NOT be copied to a linked collection. 
This is a limitation of the system that I haven't found a way around, but I did add a sort of hacky solution to it by adding an obscurely named "Unhide hidden objects" toggle.
If you activate this prior to creating a linked collection, ALL objects in the collection will be unhidden prior to the creation of the linked collection.
Just be aware that they won't change their position when selecting all objects in a collection, as they are not selectable once they are hidden.

## Tool 2: Sync Active Object

Add an object to a collection and sync that new object to all linked collections - while retaining its relative position, scale and rotation,
by selecting a reference object.

![3](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/75b24181-2e2f-40d5-985e-383a8420b917)

You can also choose which collections to sync to by selecting specific collections prior to syncing.
_(Note: Currently only one collection can be selected as the target, WIP !)_

1. Select the collection you want to sync to
2. Select the reference object for retaining relative scale, rotation & position of the object that is to be synced
3. Select the object to be synced
   
![4](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/aa26e0ef-61d0-4a13-9644-93df8bc15f82)

## Tool 3: Remove Active Object

Allows to remove the active object from all linked collections (but keeps it in the current one).

![5](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/034f59cc-1ed8-4bdc-a675-fb1b58dea23d)

## QOL Tools

I added a couple of QOL Tools; some of them are build-in tools that I just moved into the add-on so I have quick access to them.

- Select all objects in a collection directly from the viewport (saves the need to go into the hierarchy)
- Set the active collection based on the currently active object (again, a bit quicker for me than doing it in the hierarchy)

Two of these tools deserve a bit more explaination:

**Disable selected in viewport**
This saves you from going into the Details panel > Object > Visibility > Hide in Viewports. This is actually different from just using the eye icon in the Hierarchy, confusingly.
I use this in my workflow because I'm importing blender files directly into Unity, and hiding objects (e.g. boolean helper objects) by using the Eye icon doesn't hide them in Unity; using the Visibilty setting in the details panel does, however.
The included tool not only saves you from having to go into that menu but also allows to hide multiple objects at the same time by selecting them.

**Set Origin to Geometry:**
This one is actually very useful and fixes an issue with using the standard way of setting the origin to geometry with linked collections.
If you want to set your object's origin to be at the center, doing it the normal way will result in changing the positions of linked objects. This happens for ... Blender reasons?
I wrote some logic to prevent that from happening with this tool.

![6](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/e5aa2184-2106-4b11-b195-532f5db0bf5a)
