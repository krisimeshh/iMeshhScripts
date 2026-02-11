import bpy
from mathutils import Vector


class IMESHH_OT_cursor_to_bounds(bpy.types.Operator):
    """Place 3D cursor at combined bounding box center of selected objects and set origin"""
    bl_idname = "imeshh.cursor_to_bounds"
    bl_label = "Cursor to Bounds of Selection"
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

    def get_bounds_center(self, obj, bottom=False):
        """Get bounding box center (or bottom center) for a single object"""
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

    def execute(self, context):
        objs = context.selected_objects
        objs = [o for o in objs if getattr(o, "bound_box", None)]

        if not objs:
            self.report({"WARNING"}, "No selected objects with bounding boxes")
            return {"CANCELLED"}

        # Store original cursor location
        original_cursor = context.scene.cursor.location.copy()

        if self.set_origin:
            # Process each object individually
            for obj in objs:
                target = self.get_bounds_center(obj, self.bottom_center)

                # Move cursor to this object's target
                context.scene.cursor.location = target

                # Deselect all, select only this object
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj

                # Set origin to cursor
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
            # Just move cursor to combined bounds center
            big = 1e10
            mins = Vector((big, big, big))
            maxs = Vector((-big, -big, -big))

            for o in objs:
                mat = o.matrix_world
                for v in o.bound_box:
                    wp = mat @ Vector(v)
                    mins.x = min(mins.x, wp.x)
                    mins.y = min(mins.y, wp.y)
                    mins.z = min(mins.z, wp.z)
                    maxs.x = max(maxs.x, wp.x)
                    maxs.y = max(maxs.y, wp.y)
                    maxs.z = max(maxs.z, wp.z)

            center = (mins + maxs) * 0.5
            if self.bottom_center:
                target = Vector((center.x, center.y, mins.z))
            else:
                target = center

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


class IMESHH_PT_cleaner_cursor(bpy.types.Panel):
    bl_label = "Cursor Tools"
    bl_idname = "IMESHH_PT_cleaner_cursor"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "i-Meshh Cleaner"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator(
            "imeshh.cursor_to_bounds",
            text="Cursor to Bounds of Selection",
            icon="PIVOT_CURSOR",
        )


classes = (
    IMESHH_OT_cursor_to_bounds,
    IMESHH_PT_cleaner_cursor,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
