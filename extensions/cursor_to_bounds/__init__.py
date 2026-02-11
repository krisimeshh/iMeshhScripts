import bpy
from mathutils import Vector


def get_combined_bounds(objs, bottom=False):
    """Get combined bounding box center (or bottom center) for multiple objects."""
    big = 1e10
    mins = Vector((big, big, big))
    maxs = Vector((-big, -big, -big))

    for obj in objs:
        mat = obj.matrix_world
        for v in obj.bound_box:
            wp = mat @ Vector(v)
            mins.x = min(mins.x, wp.x)
            mins.y = min(mins.y, wp.y)
            mins.z = min(mins.z, wp.z)
            maxs.x = max(maxs.x, wp.x)
            maxs.y = max(maxs.y, wp.y)
            maxs.z = max(maxs.z, wp.z)

    center = (mins + maxs) * 0.5

    if bottom:
        return Vector((center.x, center.y, mins.z))
    return center


def get_single_bounds(obj, bottom=False):
    """Get bounding box center (or bottom center) for a single object."""
    big = 1e10
    mins = Vector((big, big, big))
    maxs = Vector((-big, -big, -big))

    mat = obj.matrix_world
    for v in obj.bound_box:
        wp = mat @ Vector(v)
        mins.x = min(mins.x, wp.x)
        mins.y = min(mins.y, wp.y)
        mins.z = min(mins.z, wp.z)
        maxs.x = max(maxs.x, wp.x)
        maxs.y = max(maxs.y, wp.y)
        maxs.z = max(maxs.z, wp.z)

    center = (mins + maxs) * 0.5

    if bottom:
        return Vector((center.x, center.y, mins.z))
    return center


class IMESHH_OT_cursor_to_combined_bounds(bpy.types.Operator):
    """Move 3D cursor to the combined bounding box center of all selected objects"""
    bl_idname = "imeshh.cursor_to_combined_bounds"
    bl_label = "Cursor to Combined Bounds Center"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        objs = [o for o in context.selected_objects if getattr(o, "bound_box", None)]

        if not objs:
            self.report({"WARNING"}, "No selected objects with bounding boxes")
            return {"CANCELLED"}

        target = get_combined_bounds(objs)
        context.scene.cursor.location = target
        self.report({"INFO"}, f"Cursor moved to combined bounds center")

        return {"FINISHED"}


class IMESHH_OT_cursor_to_bounds(bpy.types.Operator):
    """Place 3D cursor at bounding box center per object and optionally set origin"""
    bl_idname = "imeshh.cursor_to_bounds"
    bl_label = "Cursor to Bounds & Set Origin"
    bl_options = {"REGISTER", "UNDO"}

    set_origin: bpy.props.BoolProperty(
        name="Set Origin to Center",
        description="Move the origin of selected objects to the bounding box center",
        default=True,
    )

    bottom_center: bpy.props.BoolProperty(
        name="Use Bottom Center",
        description="Set origin to bottom center of bounding box instead of true center",
        default=False,
    )

    move_to_world_origin: bpy.props.BoolProperty(
        name="Move to World Origin",
        description="After setting origin, move objects to 0,0,0",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        objs = [o for o in context.selected_objects if getattr(o, "bound_box", None)]

        if not objs:
            self.report({"WARNING"}, "No selected objects with bounding boxes")
            return {"CANCELLED"}

        original_cursor = context.scene.cursor.location.copy()

        if self.set_origin:
            for obj in objs:
                target = get_single_bounds(obj, self.bottom_center)

                context.scene.cursor.location = target

                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj

                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                if self.move_to_world_origin:
                    obj.location = Vector((0, 0, 0))

            # Restore selection
            for obj in objs:
                obj.select_set(True)

            if self.move_to_world_origin:
                context.scene.cursor.location = Vector((0, 0, 0))
                self.report({"INFO"}, "Origins set and objects moved to world origin")
            else:
                context.scene.cursor.location = original_cursor
                self.report({"INFO"}, f"Origins set to {'bottom center' if self.bottom_center else 'center'}")
        else:
            target = get_combined_bounds(objs, self.bottom_center)
            context.scene.cursor.location = target
            self.report({"INFO"}, f"Cursor moved to {target}")

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "set_origin")

        col = layout.column()
        col.enabled = self.set_origin
        col.prop(self, "bottom_center")
        col.prop(self, "move_to_world_origin")


class IMESHH_PT_cursor_tools(bpy.types.Panel):
    bl_label = "Cursor Tools"
    bl_idname = "IMESHH_PT_cursor_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "iMeshh"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator(
            "imeshh.cursor_to_combined_bounds",
            text="Cursor to Combined Bounds",
            icon="PIVOT_CURSOR",
        )
        col.operator(
            "imeshh.cursor_to_bounds",
            text="Cursor to Bounds & Set Origin",
            icon="OBJECT_ORIGIN",
        )


classes = (
    IMESHH_OT_cursor_to_combined_bounds,
    IMESHH_OT_cursor_to_bounds,
    IMESHH_PT_cursor_tools,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
