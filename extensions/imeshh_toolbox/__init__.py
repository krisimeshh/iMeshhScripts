import bpy

from . import cursor_tools
from . import uv_tools


# ---------------------------------------------------------------------------
# Parent panel — all tool sub-panels nest under this
# ---------------------------------------------------------------------------

class IMESHH_PT_toolbox(bpy.types.Panel):
    bl_label = "iMeshh Toolbox"
    bl_idname = "IMESHH_PT_toolbox"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "iMeshh"

    def draw(self, context):
        pass  # sub-panels provide the content


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

# Collect all modules that expose a `classes` tuple.
# To add a new tool category, create a module with operators + a sub-panel
# and add it to this list.
_modules = (
    cursor_tools,
    uv_tools,
)


def register():
    bpy.utils.register_class(IMESHH_PT_toolbox)
    for mod in _modules:
        for cls in mod.classes:
            bpy.utils.register_class(cls)


def unregister():
    for mod in reversed(_modules):
        for cls in reversed(mod.classes):
            bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(IMESHH_PT_toolbox)
