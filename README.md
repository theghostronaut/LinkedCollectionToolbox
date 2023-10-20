# LinkedCollectionToolbox
A Blender plugin for better linked collections (Compatibility checked with 3.6.1)

## Tool 1: Create Linked Collection
Creates a linked collection from the currently active object, organising and naming it and selecting all the objects in the new collection

![1](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/7b6964c4-9b4b-4d90-ae41-98725ccb62ff)

Changes made to objects in Edit mode will by synced to all linked collections, as usual.

![2](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/2d4ebe2c-ffaa-48ad-954e-fa78fac54a4f)

There is one thing to be aware of: Blender doesn't actually link the collection but rather only the objects. My add-on handles all of that internally.
But the issue here is that objects that are set to be hidden from the viewport (not those hidden with the Eye icon but hidden via Object>Visibility!) will NOT be copied to a linked collection. 
This is a limitation of the system that I haven't found a way around, but I did add a sort of hacky solution to it by adding an obscurely named "Unhide hidden objects" toggle.
If you activate this prior to creating a linked collection, ALL objects in the collection will be unhidden prior to the creation of the linked collection.
Just be aware that they won't change their position when selecting all objects in a collection, as they are not selectable once they are hidden.

## Tool 2: Sync Active Object

Add an object to a collection and sync that new object to all linked collections - while retaining its relative position, scale and rotation,
by selecting a reference object.

![3](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/1158cff4-88c0-4b09-951a-53590d79e1e9)

You can also choose which collections to sync to by selecting specific collections prior to syncing.
_(Note: Currently only one collection can be selected as the target, WIP !)_

1. Select the collection you want to sync to
2. Select the reference object for retaining relative scale, rotation & position of the object that is to be synced
3. Select the object to be synced
   
![4](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/bdac1912-7acc-4eca-b887-fe913d04b26f)

## Tool 3: Remove Active Object

Allows to remove the active object from all linked collections (but keeps it in the current one).

![5](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/9f1d1a74-b9b7-4fc8-a2bb-72f49210f357)

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

# Installation
Download linked_collection_toolbox.py, add it to Blender Addons (Edit > Preferences > Add-ons > "Install") and activate it.
A new tab "Linked Collection Toolbox" will be added to the Viewport toolbar (N)

I wrote some logic to prevent that from happening with this tool.

![6](https://github.com/theghostronaut/LinkedCollectionToolbox/assets/57066443/85e16212-5585-4b97-88c0-998c62a9f3f9)
