import bpy
import bmesh


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class IMESHH_OT_select_flipped_uvs(bpy.types.Operator):
    """Select faces whose UV islands are flipped (negative winding order)"""
    bl_idname = "imeshh.select_flipped_uvs"
    bl_label = "Select Flipped UVs"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def execute(self, context):
        obj = context.active_object

        prev_mode = obj.mode
        if prev_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        # Deselect everything first
        for face in bm.faces:
            face.select = False
            for loop in face.loops:
                loop[uv_layer].select = False
                loop[uv_layer].select_edge = False

        count = 0
        for face in bm.faces:
            uvs = [loop[uv_layer].uv for loop in face.loops]

            # Compute signed area via the shoelace formula
            area = 0.0
            n = len(uvs)
            for i in range(n):
                j = (i + 1) % n
                area += uvs[i].x * uvs[j].y
                area -= uvs[j].x * uvs[i].y

            if area < 0:
                count += 1
                face.select = True
                for loop in face.loops:
                    loop[uv_layer].select = True
                    loop[uv_layer].select_edge = True

        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)

        for area in context.screen.areas:
            area.tag_redraw()

        self.report({"INFO"}, f"Selected {count} flipped UV face(s)")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Sub-panel
# ---------------------------------------------------------------------------

class IMESHH_PT_uv_tools(bpy.types.Panel):
    bl_label = "UV Tools"
    bl_idname = "IMESHH_PT_uv_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "iMeshh"
    bl_parent_id = "IMESHH_PT_toolbox"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator(
            "imeshh.select_flipped_uvs",
            text="Select Flipped UVs",
            icon="UV",
        )


# ---------------------------------------------------------------------------
# Registration list
# ---------------------------------------------------------------------------

classes = (
    IMESHH_OT_select_flipped_uvs,
    IMESHH_PT_uv_tools,
)
