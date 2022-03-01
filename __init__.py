bl_info = {
	"name": "Compositor Quick File Output Name",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (3, 0, 0),
	"location": "Compositor > Context Menu",
	"description": "Quickly names output slots from selected image.",
	"warning": "",
	"wiki_url": "",
	"category": "Compositor"
}

import bpy
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty, BoolProperty, FloatProperty, StringProperty, PointerProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel, AddonPreferences

"""
General Notes to Self
list(scene.somethingbig) - To see arrays in console

##Props
options = {
	"HIDDEN", # Hidden from UI, good for operators
	"SKIP_SAVE", # This prop is not saved in presets
	"ANIMATABLE",
	"LIBRARY_EDITABLE", # This prop can edited from linked instances (changes not saved)
	"PROPORTIONAL", # 
	"TEXTEDIT_UPDATE"
}

#Number
min, max, soft_min, soft_max
unit = "LENGTH", "AREA", "VOLUME", "ROTATION", "TIME", "VELOCITY", "ACCELERATION", "MASS", "CAMERA", "POWER"
subtype = "PIXEL", "UNSIGNED", "PERCENTAGE", "FACTOR", "ANGLE", "TIME", "DISTANCE", "DISTANCE_CAMERA"
"POWER", "TEMPERATURE"

#Float
precision = 3 # display precision
subtype = ""

#XVector
size = 3
subtype = "COLOR" , "TRANSLATION", "DIRECTION", "VELOCITY", "ACCELERATION", "MATRIX", "EULER"
"QUATERNION", "AXISANGLE", "XYZ", "XYZ_LENGTH", "COLOR_GAMMA", "COORDINATES", "LAYER"
"LAYER_MEMBER"

#String
subtype = "DIR_PATH", "FILE_PATH", "FILE_NAME", "BYTE_STRING", "PASSWORD"

#Enum
Dynamic
def get_enum_items(self, context):
	enum_list = []
	
	for obj in context.selected_objects:
		enum_list.append( (obj.name, obj.name, "") )
	
	return enum_list
obj_name : EnumProperty(items=get_enum_items, name="Object Name")
Static
obj_name : EnumProperty(
	items=[
		("ITEM","Item Name", "Item Description", "UI_ICON", 0),
		("ITEM2","Item Name2", "Item Description", "UI_ICON", 1)
	],
	name="Object Name",
	description=""
)

##Collections
context.scene.collection - Master Scene collection
context.collection - Active Collection
collection.all_objects - all objects in this and child collections
collection.objects - objects in this collection
collection.children - child collections
collection.children.link(collection2) - link collection2 as child of collection
	will throw error if already in collection
collection.children.unlink(collection2) - unlink collection2 as child of collection
collection.objects.link(obj) - link object to collection
collection.objects.unlink(obj) - unlink object

##Window
context.area.type - Type of area

Window Manager
context.window_manager

"""

## Constants
# Set to true when debugging, enables debug print statements and stuff
DEBUGGING = True


## Helper Functions
def get_addon_preferences():
	return bpy.context.preferences.addons[__package__].preferences

def dprint(print_string):
	# print debug string
	if DEBUGGING:
		print(f"[DEBUG] {__package__}: {print_string}")


## Structs
#class SA_Settings(PropertyGroup):
#	pass


## Operators
class QON_OT_quick_output_name(Operator):
	"""Names selected file output's subpaths to selected image name"""
	bl_idname = "qon.quick_output_name"
	bl_label = "Quick Output Name"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		return True

	# Dialog invoke
	#def invoke(self, context, event):
	#	return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		# Get selected nodes from compositor
		selected_nodes = (node for node in context.scene.node_tree.nodes if node.select)

		# Init image and output nodes
		image_node = output_node = None
		for node in selected_nodes:
			if node.type == "IMAGE":
				image_node = node
			elif node.type == "OUTPUT_FILE":
				output_node = node

		# make sure both arent None
		if None in (image_node, output_node):
			self.report({"ERROR"}, "Image or File Output not selected!")
			return {"CANCELLED"}
		
		# create file slots if needed
		while( len(output_node.file_slots) < 2 ):
			# set blank subpath for now, we will set the subpaths later
			output_node.file_slots.new("")
		
		# get image name
		image_name = image_node.image.name
		
		# remove file extension
		image_name = image_name[:image_name.rfind(".")]

		# set subpaths
		composite_name = f"{image_name}_Composited"
		wireframe_name = f"Wireframe_{composite_name}"

		output_node.file_slots[0].path = composite_name
		output_node.file_slots[1].path = wireframe_name

		return {'FINISHED'}


## Append to UI Helper Functions
def draw_func(self, context):
	#layout = self.layout
	self.layout.operator(QON_OT_quick_output_name.bl_idname)


## Preferences
class QON_addon_preferences(AddonPreferences):
	bl_idname = __package__
	
	# Properties
	show_mini_manual : BoolProperty(name="Show Mini Manual", default=False)

	def draw(self, context):
		layout = self.layout
		
		layout.prop(self, "show_mini_manual", toggle=True)
		
		if self.show_mini_manual:
			layout.label(text="Using", icon="DOT")
			layout.label(text="Select both image and file output nodes in compositor.",icon="THREE_DOTS")
			layout.label(text="Run Quick Output Name from right click context menu or from operator search.",icon="THREE_DOTS")


## Register
classes = (
	QON_OT_quick_output_name,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	## Add Custom Properties
	#bpy.types.WindowManager.something = PointerProperty(type=SA_PropertyGroup) # to not save things with blend file
	#bpy.types.Scene.something = PointerProperty(type=SA_PropertyGroup)
	
	## Append to UI
	bpy.types.NODE_MT_context_menu.append(draw_func)

def unregister():
	## Remove from UI
	bpy.types.NODE_MT_context_menu.remove(draw_func)
	
	## Remove Custom Properties
	#del bpy.types.Scene.something
	#del bpy.types.WindowManager.something
	
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()
