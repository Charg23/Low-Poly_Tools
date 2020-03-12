# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# notes:
#   - Works in Edit mode and Object mode of MESH type.
#     in Add-on Preferences, can change the button item that is displayed in Tool Shelf.
#
#   - this Tool was made by kagayas <kagayasusi@gmail.com> on the basis of "Retopology Tools Extend".
#     (reduce some function, add some feature for low-poly modelling)
#
#   - Necessary Add-ons(optional)
#      * Auto Mirror > http://le-terrier-de-lapineige.over-blog.com/2014/07/automirror-mon-add-on-pour-symetriser-vos-objets-rapidement.html
#      * LoopTools
#      * Easy Lattice > http://kagayas.com/bl_easy-lattice_addon/

# changelog:
# 2016.01.23 renewal version release
# 2020.03.08 support blender 2.8 by Charg
#   -   can remove key bind at AddonPreferences
import bpy
#from bpy.props import *
from bpy.props import BoolProperty, IntProperty, EnumProperty, PointerProperty
from bpy.app.translations import pgettext_iface as iface_
from bpy.types import Operator, Panel, AddonPreferences, PropertyGroup
import bmesh
from mathutils import *
import math

bl_info = {
    "name": "Low-Poly Tools",
    "author": "kagayas",  # "Cédric Lepiller for basic layout" "Gert De Roost for the Laprelax code" "Jordiart > Display Tools / mkb reorder"
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Tool Shelf > Low-Poly tab",
    "description": "Tools for low-poly modelling",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}

translation_dict = {
    "ja_JP": {
        ("*", "Tools for low-poly modelling"): "ローポリモデリングのためのツールパネル",
        ("*", "3D View > Tool Shelf > Low-Poly tab"): "3Dビュー > ツールシェルフ > ローポリタブ",
        ("*", "Low-Poly Tools"): "ローポリ用ツール",
        ("*", "Low-Poly"): "ローポリ",
        ("Operator", "Auto Mirror"): "ミラーをセットアップ",
        ("Operator", "Wire All"): "すべてのワイヤーを表示",
        ("*", "Show wireframe all objects"): "すべてのオブジェクトのワイヤフレームを表示します",
        ("*", "Render and display object flat or smooth"): "オブジェクトの表示をフラット・スムーズにします",
        ("*", "Easy Lattice:"): "イージーラティス:",
        ("Operator", "Align X"): "X軸を揃える",
        ("Operator", "Align Y"): "Y軸を揃える",
        ("Operator", "Align Z"): "Z軸を揃える",
        ("*", "Align selected vertices to X axis"): "選択した頂点のX軸を揃えます",
        ("*", "Align selected vertices to Y axis"): "選択した頂点のY軸を揃えます",
        ("*", "Align selected vertices to Z axis"): "選択した頂点のZ軸を揃えます",
        ("Operator", "Edge Rotate"): "辺を回転",
        ("Operator", "Face Rotate"): "四角面を回転",
        ("*", "Rotate selected face"): "選択した四角面を回転します",
        ("Operator", "Bridge"): "ブリッジ",
        ("Operator", "LapRelax"): "リラックス",
        ("*", "Smoothing mesh keeping volume"): "形状を維持しつつ平滑化します",
        ("Operator", "Symmetrize X Axis"): "X軸で対称化",
        ("*", "Enforce symmetry across X axis"): "X軸で対称にします",
        ("Operator", "Snap to Symmetry X Axis"): "X軸で対象にスナップ",
        ("*", "Snap vertex pairs to their mirrored X axis"): "頂点のペアをX軸でミラー反転した位置にスナップします",
        ("Operator", "Toggle AutoMerge"): "自動結合を切り替え",
        ("*", "Toggle AutoMerge and vertex snap at the same time"): "自動結合と頂点スナップを同時に切り替えます",
        ("*", "LoopTools:"): "ループツールズ:",
        ("Operator", "Flatten"): "平面化",
        ("Operator", " Circle "): "円形化",
        ("Operator", "Curve"): "カーブ",
        ("Operator", "Loft"): "ロフト",
        ("Operator", "Space"): "等間隔",
        ("*", "Gstretch"): "Gストレッチ",
        ("*", "Flatten vertices on a best-fitting plane"): "頂点を最適な平面で平らにします",
        ("*", "Move selected vertices into a circle shape"): "選択頂点を円形状に移動します",
        ("*", "Bridge two, or loft several, loops of vertices"): "2つ以上のエッジループをブリッジ・ロフトします",
        ("*", "Turn a loop into a smooth curve"): "エッジループを滑らかにします",
        ("*", "Space the vertices in a regular distrubtion on the loop"): "エッジループ上の頂点を等間隔にします",
        ("*", "Relax the loop, so it is smoother"): "エッジループをリラックスします",
        ("*", "Stretch selected vertices to Grease Pencil stroke"): "選択した頂点をグリースペンシルストロークにストレッチします",
        ("*", "Mark Edge:"): "辺に印を付ける:",
        ("Operator", "Seam"): "シーム",
        ("Operator", "Sharp"): "シャープ",
        ("Operator", "Cylinder Projection Ex"): "円筒状投影 Ex",
        ("*", "Cylinder projection improved the center of projection"): "投影の中心点を改善した円筒状投影",
        ("*", "Center of projection"): "投影の中心",
        ("*", "to center the position of the 3D cursor"): "3Dカーソルの位置を中心にする",
        ("*", "Origin to Selection"): "原点を選択へ移動",
        ("*", "Origin to Center of Axis"): "原点を軸の中心に移動",
        ("*", "Set the object's origin"): "原点を再設定します",
        ("Operator", "Add key bind for select mode"): "編集モードの選択切替キーを追加",
        ("Operator", "Remove key bind for select mode"): "編集モードの選択切替キーを削除"
    }
}


#----------------------------------------------------


class LowpolyToolsPrefs(AddonPreferences):
    bl_idname = __name__

    show_rotate : BoolProperty(name="Rotate", default=True)
    show_symmetry : BoolProperty(name="Symmetry", default=True)
    show_flatten : BoolProperty(name="Flatten", default=True)
    show_gstretch : BoolProperty(name="Gstretch", default=True)

    show_undo : BoolProperty(name="History", default=False)
    show_data : BoolProperty(name="Data Transfer", default=False)
    show_select : BoolProperty(name="Select", default=True)
    show_xyz : BoolProperty(name="X Y Z", default=True)
    
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Show:")

        col = layout.column_flow(columns=4)
        col.prop(self, 'show_undo')
        col.prop(self, 'show_data')
        col.prop(self, 'show_select')
        col.prop(self, 'show_xyz')
        col.prop(self, 'show_rotate')
        col.prop(self, 'show_symmetry')
        col.prop(self, 'show_flatten')
        col.prop(self, 'show_gstretch')
        
        
        layout.label(text="Key bind:")
        col = layout.column()
        if len(addon_keymaps) == 0:
            col.operator('toggle.key_bind',text ='Add key bind for select mode' )
        else:
            col.operator('toggle.key_bind',text ='Remove key bind for select mode' )
        #addon_keymaps


class LowpolyTools_Properties(PropertyGroup):

    @classmethod
    def register(cls):
        bpy.types.Scene.lowpoly_tools_props = PointerProperty(type=cls)

        cls.disp_tools = BoolProperty(
            name="Display Tools",
            description="Display settings of the Tools",
            default=True
        )
        cls.disp_looptools = BoolProperty(
            name="Display LoopTools",
            description="Display settings of the LoopTools",
            default=True
        )
        cls.disp_easy_lattice = BoolProperty(
            name="Display Easy Lattice",
            description="Display settings of the Easy Lattice",
            default=True
        )
        cls.disp_mark_edge = BoolProperty(
            name="Display Mark Edge",
            description="Display settings of the Mark Edge",
            default=True
        )
        cls.disp_shading = BoolProperty(
            name="Display Shading",
            description="Display settings of the Shading",
            default=True
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.lowpoly_tools_props


#----------------------------------------------------


# LapRelax
class LPT_OT_LapRelax(Operator):
    '''Smoothing mesh keeping volume'''
    bl_idname = 'mesh.laprelax'
    bl_label = "LapRelax"
    bl_options = {'REGISTER', 'UNDO'}

    Repeat : IntProperty(
        name="Repeat",
        description="Repeat how many times",
        default=1, min=1, max=10,
        options={'SKIP_SAVE'}
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):
        # smooth # Repeat times
        for i in range(self.Repeat):
            self.do_laprelax(context)
        return {'FINISHED'}

    def do_laprelax(self, context):
        obj = context.active_object
        mesh = obj.data

        bm = bmesh.from_edit_mesh(mesh)
        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 73:
            bm.verts.ensure_lookup_table()

        bmprev = bm.copy()

        for v in bmprev.verts:
            if v.select:
                tot = Vector((0, 0, 0))
                cnt = 0
                for e in v.link_edges:
                    for f in e.link_faces:
                        if not(f.select):
                            cnt = 1
                    if len(e.link_faces) == 1:
                        cnt = 1
                        break
                if cnt:
                    # dont affect border edges: they cause shrinkage
                    continue

                # find Laplacian mean
                for e in v.link_edges:
                    tot += e.other_vert(v).co
                tot /= len(v.link_edges)

                # cancel movement in direction of vertex normal
                delta = (tot - v.co)
                if delta.length != 0:
                    ang = delta.angle(v.normal)
                    deltanor = math.cos(ang) * delta.length
                    nor = v.normal
                    nor.length = abs(deltanor)
                    bm.verts[v.index].co = tot + nor

        bmesh.update_edit_mesh(mesh, True)
        bmprev.free()


# Show wire all objects
class LPT_OT_Wire_All(Operator):
    '''Show wireframe all objects'''
    bl_idname = 'object.wire_all'
    bl_label = "Wire All"

    def execute(self, context):
        toggle = {}
        for obj in context.scene.objects:
        #for obj in context.scene.collection.objects:
            # Toggle show
            obj.show_wire = toggle.setdefault('showStatus', not obj.show_wire)
            obj.show_all_edges = toggle.setdefault('showStatus', not obj.show_wire)
        return {'FINISHED'}


# Flat Vertex to XYZ
class LPT_OT_alignx(Operator):
    '''Align selected vertices to X axis'''
    bl_label = "Align X"
    bl_idname = 'mesh.face_align_x'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tslot = context.scene.transform_orientation_slots[0]#  tslot.typeからトランスフォーム座標系を取得。元は'GLOBAL'固定
        if not tslot.use:
            bpy.ops.transform.resize(value=(0, 1, 1), constraint_axis=(True, False, False), orient_type=   tslot.type,
                                 mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
        else :
            bpy.ops.transform.resize(value=(0, 1, 1), constraint_axis=(True, False, False), orient_type='GLOBAL',orient_matrix_type='GLOBAL',
                                 mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 orient_matrix=tslot.custom_orientation.matrix)
        return {"FINISHED"}


class LPT_OT_aligny(Operator):
    '''Align selected vertices to Y axis'''
    bl_label = "Align Y"
    bl_idname = 'mesh.face_align_y'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tslot = context.scene.transform_orientation_slots[0]
        if not tslot.use:
            bpy.ops.transform.resize(value=(1, 0, 1), constraint_axis=(False, True, False), orient_type=   tslot.type,
                                 mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
        else :
            bpy.ops.transform.resize(value=(1, 0, 1), constraint_axis=(False, True, False), orient_type='GLOBAL',orient_matrix_type='GLOBAL',
                                 mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 orient_matrix=tslot.custom_orientation.matrix)
        return {"FINISHED"}


class LPT_OT_alignz(Operator):
    '''Align selected vertices to Z axis'''
    bl_label = "Align Z"
    bl_idname = 'mesh.face_align_z'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tslot = context.scene.transform_orientation_slots[0]
        if not tslot.use:
            bpy.ops.transform.resize(value=(1, 1, 0), constraint_axis=(False, False, True), orient_type=   tslot.type,
                                 mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1)
        else :
            bpy.ops.transform.resize(value=(1, 1, 0), constraint_axis=(False, False, True), orient_type='GLOBAL',orient_matrix_type='GLOBAL',
                                 mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 orient_matrix=tslot.custom_orientation.matrix)
        return {"FINISHED"}


class LPT_OT_SymmetrizeMerge(Operator):
    '''Enforce symmetry across X axis'''
    bl_idname = 'mesh.symmetrize_merge'
    bl_label = "Symmetrize X Axis"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        num = mesh.total_vert_sel
        if num == 0:
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(mesh)
        x_list = [v.co[0] for v in bm.verts if v.select]

        average = sum(x_list) / num
        direct = 'NEGATIVE_X' if average < 0 else 'POSITIVE_X'

        bpy.ops.mesh.symmetrize(direction=direct, threshold=0.0001)
        bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=True)

        return {'FINISHED'}


class LPT_OT_SymmetrySnapX(Operator):
    '''Snap vertex pairs to their mirrored X axis'''
    bl_idname = 'mesh.symmetry_snap_x'
    bl_label = "Snap to Symmetry X Axis"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        num = mesh.total_vert_sel
        if num == 0:
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(mesh)
        active = bm.select_history.active
        if active is None:
            self.report({'ERROR'}, "Mesh has no active vert/edge/face")
            return {'CANCELLED'}

        average = 0

        # Face or Edge
        if isinstance(active, bmesh.types.BMFace) or isinstance(active, bmesh.types.BMEdge):
            x_list = [v.co[0] for v in active.verts]
            average = sum(x_list) / len(x_list)

        # Vertex
        elif isinstance(active, bmesh.types.BMVert):
            average = active.co[0]

        fac = 1.0 if average < 0 else 0.0

        bpy.ops.mesh.symmetry_snap(direction='NEGATIVE_X', threshold=1.0, factor=fac, use_center=True)
        mesh.update()

        return {'FINISHED'}


# Set Smooth
class LPT_OT_SetSmooth(Operator):
    '''Render and display object flat or smooth'''
    bl_idname = 'mesh.set_smooth'
    bl_label = "Set Smooth"

    clear : BoolProperty(
        name="Clear",
        description="Smooth Clear.",
        default=False,
        options={'SKIP_SAVE'}
    )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        if self.clear:
            bpy.ops.object.shade_flat()
        else:
            bpy.ops.object.shade_smooth()
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


# Toggle Merge Vertices
class LPT_OT_ToggleMergeVertices(Operator):
    '''Toggle AutoMerge and vertex snap at the same time'''
    bl_label = "Toggle AutoMerge"
    bl_idname = 'mesh.toggle_merge_vertices'

    def execute(self, context):
        settings = context.scene.tool_settings
        if settings.use_mesh_automerge == True:
            settings.use_snap = False
            settings.use_mesh_automerge = False
            settings.snap_elements = {'INCREMENT'}
        else:
            settings.use_snap = True
            settings.use_mesh_automerge = True
            settings.snap_elements = {'VERTEX'}

        return {"FINISHED"}


# Rotate Face
class LPT_OT_FaceRotate(Operator):
    '''Rotate selected face'''
    bl_idname = 'mesh.face_rotate'
    bl_label = "Face Rotate"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.tool_settings.mesh_select_mode[2]

    def execute(self, context):
        bpy.ops.mesh.quads_convert_to_tris(quad_method='FIXED_ALTERNATE', ngon_method='BEAUTY')
        try:
            bpy.ops.mesh.edge_rotate(use_ccw=False)
        except:
            pass
        bpy.ops.mesh.tris_convert_to_quads()
        return {'FINISHED'}


# Set Vertex Mode
class LPT_OT_SetVertex(Operator):
    '''Set vertex mode'''
    #bl_idname = 'LPT_OT_SetVertex'
    bl_idname = 'mode.set_vertex'
    bl_label = "Set Vertex Mode"

    def execute(self, context):
        if bpy.ops.mesh.select_mode.poll():
            bpy.ops.mesh.select_mode(type='VERT')
        return {'FINISHED'}


# Set Edge Mode
class LPT_OT_SetEdge(Operator):
    '''Set edge mode'''    
    #bl_idname = 'LPT_OT_SetEdge'
    bl_idname = 'mode.set_edge'
    bl_label = "Set Edge Mode"

    def execute(self, context):
        if bpy.ops.mesh.select_mode.poll():
            bpy.ops.mesh.select_mode(type='EDGE')
        return {'FINISHED'}


# Set Face Mode
class LPT_OT_SetFace(Operator):
    '''Set face mode'''
    #bl_idname = 'LPT_OT_SetFace'
    bl_idname = 'mode.set_face'
    bl_label = "Set Face Mode"

    def execute(self, context):
        if bpy.ops.mesh.select_mode.poll():
            bpy.ops.mesh.select_mode(type='FACE')
        return {'FINISHED'}


# Cylinder Projection Ex
class LPT_OT_CylinderProjectionEx(Operator):
    '''Cylinder projection improved the center of projection'''
    #bl_idname = 'LPT_OT_CylinderProjectionEx'
    bl_idname = 'uv.cylinder_projection_ex'
    bl_label = "Cylinder Projection Ex"
    bl_options = {'REGISTER', 'UNDO'}

    cursor : BoolProperty(
        name="3D Cursor",
        description="to center the position of the 3D cursor",
        default=False
    )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):
        try:
            obj = context.active_object
            scene = context.scene

            saved_origin = obj.location.copy()
            saved_location = scene.cursor_location.copy()  # returns a copy of the vector

            # set the origin
            if self.cursor == False:
                bpy.ops.view3d.snap_cursor_to_selected()
            origin_set()

            # uv mapping
            bpy.ops.uv.cylinder_project(scale_to_bounds=True)
            scene.cursor_location = saved_origin
            origin_set()

            # back to the stored location
            scene.cursor_location = saved_location
        except:
            pass
        return {'FINISHED'}

    def draw(self, context):
        self.layout.label(text="Center of projection")
        self.layout.prop(self, 'cursor')


# Origin Set
def origin_set(mode='EDIT'):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.mode_set(mode=mode)


class LPT_OT_MeshSetOrigin(Operator):
    '''Set the object's origin'''
    #bl_idname = 'lpt.meshsetorigin'
    bl_idname = 'mesh.origin_set'
    bl_label = "Set Origin"
    bl_options = {'REGISTER', 'UNDO'}

    type : EnumProperty(
        name="Type",
        items=(
            ('ORIGIN_SELECTION', "Origin to Selection", "", 'RESTRICT_SELECT_OFF', 1),
            ('ORIGIN_CURSOR', "Origin to 3D Cursor", "", 'CURSOR', 2),
            ('ORIGIN_CENTER', "Origin to Center of Axis", "", 'ORIENTATION_GLOBAL', 3),
        ))

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH')

    def execute(self, context):
        obj = context.active_object
        mode = obj.mode
        scene = context.scene
        saved_location = scene.cursor_location.copy()

        if self.type == 'ORIGIN_SELECTION':
            bpy.ops.view3d.snap_cursor_to_selected()
            origin_set(mode)

        elif self.type == 'ORIGIN_CURSOR':
            origin_set(mode)

        elif self.type == 'ORIGIN_CENTER':
            bpy.ops.view3d.snap_cursor_to_center()
            origin_set(mode)

        # back to the stored location
        scene.cursor_location = saved_location

        return {'FINISHED'}


# Dummy Function
class LPT_OT_DummyFunction(Operator):
    '''Dummy function'''
    bl_idname = 'mesh.dummy_function'
    bl_label = "Dummy Function"

    def execute(self, context):
        return {"FINISHED"}


# Toggle Occlude
class LPT_OT_ToggleOcclude(Operator):
    '''Toggle occlude'''
    bl_idname = 'mode.toggle_occlude'
    bl_label = "Toggle Occlude"

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):
        #context.space_data.use_occlude_geometry = not context.space_data.use_occlude_geometry
        bpy.ops.view3d.toggle_xray()
        return {'FINISHED'}

class LPT_OT_Keybinding(Operator):
    '''Key Binding'''
    bl_idname = 'toggle.key_bind'
    bl_label = "Key Binding"
    
    wm = bpy.context.window_manager

    def execute(self, context):
        
        if len(addon_keymaps) == 0:
            wm = bpy.context.window_manager
            km = wm.keyconfigs.addon.keymaps.new(name="Mesh")
            for idname, key in addon_idname:
                kmi = km.keymap_items.new(idname, key, 'PRESS')
                addon_keymaps.append((km, kmi))
        else:
            
            # Handle the keymap
            for km, kmi in addon_keymaps:
                km.keymap_items.remove(kmi)
            # Clear the list
            addon_keymaps.clear()
        return {'FINISHED'}
    
# ---------------------------------------------------
# Object Mode
# ---------------------------------------------------
class LPT_PT_LowpolyToolsObject(Panel):
    bl_label = "Low-Poly Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Low-Poly"
    #bl_idname = 'lpt.objectpanel'
    

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is not None:
            if obj.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE', 'LATTICE']:
                if obj.mode == 'OBJECT':
                    return True
        return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        view = context.space_data
        #scene = context.scene
        shading = view.shading
        addon_prefs = get_addon_prefs()

        # Basic
        if addon_prefs.show_undo:
            row = layout.row(align=True)
            row.operator('ed.undo')
            row.operator('ed.redo')

        # Tools
        layout.label(text="Tools:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator_menu_enum('object.origin_set', 'type', icon='ORIENTATION_GLOBAL')

        # Auto Mirror
        if obj.type == 'MESH' and hasattr(bpy.types, 'OBJECT_OT_automirror'):
            col.operator('object.automirror', text="Auto Mirror", icon='MOD_MIRROR')
        else:
            col.label(text="")

        # Easy Lattice
        if obj.type in ['MESH', 'LATTICE']:
            if hasattr(bpy.types, 'EasyLattice_layout'):
                layout.label(text="Easy Lattice:")
                bpy.types.EasyLattice_layout.draw(self, context)

        # Data Transfer
        if obj.type == 'MESH' and addon_prefs.show_data:
            layout.label(text="Data Transfer:")
            row = layout.row(align=True)
            row.operator('object.data_transfer', text="Data")
            row.operator('object.datalayout_transfer', text="Data Layout")

        # Shading
        layout.label(text="Shading:")
        col = layout.column(align=True)
        col.operator('object.wire_all', icon='MESH_UVSPHERE')

        row = col.row(align=True)
        row.operator('object.shade_flat', text="Flat", icon='MESH_ICOSPHERE')
        row.operator('object.shade_smooth', text="Smooth", icon='MATSPHERE')

        # Properties
        col = layout.column()
        row = col.row()
        row.prop(shading, 'show_backface_culling')
        row.prop(shading, 'light')

        if obj is not None:
            row = col.row()
            row.prop(obj, 'show_name', text="Name")
            row.prop(obj, 'show_in_front', text="In Front")


# ---------------------------------------------------
# Edit Mode
# ---------------------------------------------------
class LPT_PT_LowpolyToolsEdit(Panel):
    bl_label = "Low-Poly Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = 'mesh_edit'
    bl_category = "Low-Poly"
    #bl_idname = 'lpt.editpanel'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        view = context.space_data
        props = context.scene.lowpoly_tools_props
        addon_prefs = get_addon_prefs()
        shading = view.shading
        overlay = view.overlay
        # Basic
        if addon_prefs.show_undo:
            row = layout.row(align=True)
            row.operator('ed.undo')
            row.operator('ed.redo')

        # Tools
        row = layout.row(align=True)
        row.prop(
            props,
            'disp_tools',
            text="",
            icon='TRIA_DOWN' if props.disp_tools else 'TRIA_RIGHT',
            emboss=False
        )
        row.label(text="Tools:")

        if addon_prefs.show_select:
            row = row.row(align=True)
            row.scale_x = 3
            row.operator('mesh.select_random', text="", icon='RNDCURVE')
            row.operator('mesh.select_face_by_sides', text="", icon='VERTEXSEL')
            row.operator('mesh.edges_select_sharp', text="", icon='EDGESEL')
            row.operator('mesh.faces_select_linked_flat', text="", icon='FACESEL')
            row.menu('VIEW3D_MT_edit_mesh_select_similar', text="", icon='GROUP')

        if props.disp_tools:
            col = layout.column(align=True)

            col.operator_menu_enum('mesh.origin_set', 'type', icon='ORIENTATION_GLOBAL')

            if addon_prefs.show_xyz:
                row = col.row(align=True)
                row.operator('mesh.face_align_x', text="X", icon='SNAP_INCREMENT')
                row.operator('mesh.face_align_y', text="Y", icon='SNAP_INCREMENT')
                row.operator('mesh.face_align_z', text="Z", icon='SNAP_INCREMENT')

            if addon_prefs.show_rotate:
                row = col.row(align=True)
                row.operator('mesh.edge_rotate', text="Edge Rotate", icon='EDGESEL')
                row.operator('mesh.face_rotate', icon='FACESEL')

            row = col.row(align=True)
            row.operator('mesh.bridge_edge_loops', text="Bridge", icon='PARTICLE_PATH')
            row.operator('mesh.fill_grid', icon='OUTLINER_OB_LATTICE')

            row = col.row(align=True)
            row.operator('mesh.vertices_smooth', text="Smooth", icon='SPHERECURVE')
            row.operator('mesh.laprelax', text="LapRelax", icon='SMOOTHCURVE')

            if addon_prefs.show_symmetry:
                col.separator()
                row = col.row(align=True)
                row.operator('mesh.symmetrize_merge', text="Symmetrize", icon='MOD_MIRROR')
                row.operator('mesh.symmetry_snap_x', text="Snap", icon='ARROW_LEFTRIGHT')

            col.operator(
                'mesh.toggle_merge_vertices',
                icon='SNAP_ON' if context.scene.tool_settings.use_mesh_automerge else 'SNAP_OFF'
            )

        # LoopTools
        if hasattr(bpy.types, 'VIEW3D_PT_tools_looptools'):
            row = layout.row(align=True)
            row.prop(
                props,
                'disp_looptools',
                text="",
                icon='TRIA_DOWN' if props.disp_looptools else 'TRIA_RIGHT',
                emboss=False
            )
            row.label(text="LoopTools:")

            if props.disp_looptools:
                col = layout.column(align=True)

                if addon_prefs.show_flatten:
                    row = col.row(align=True)
                    row.operator('mesh.looptools_flatten', text="Flatten", icon='MESH_PLANE')
                    row.operator('mesh.looptools_circle', text=" Circle ", icon='MESH_CIRCLE')

                row = col.row(align=True)
                row.operator('mesh.looptools_curve', text="Curve", icon='OUTLINER_DATA_CURVE')
                row.operator('mesh.looptools_relax', text="Relax", icon='SMOOTHCURVE')

                if addon_prefs.show_gstretch:
                    row = col.row(align=True)
                    row.operator('mesh.looptools_space', text="Space", icon='ALIGN_JUSTIFY')
                    row.operator('mesh.looptools_gstretch', text=iface_("Gstretch"), icon='GREASEPENCIL')

        # Easy Lattice
        if hasattr(bpy.types, 'EasyLattice_layout'):
            row = layout.row(align=True)
            row.prop(
                props,
                'disp_easy_lattice',
                text="",
                icon='TRIA_DOWN' if props.disp_easy_lattice else 'TRIA_RIGHT',
                emboss=False
            )
            row.label(text="Easy Lattice:")

            if props.disp_easy_lattice:
                bpy.types.EasyLattice_layout.draw(self, context)

        # Mark Edge
        row = layout.row(align=True)
        row.prop(
            props,
            'disp_mark_edge',
            text="",
            icon='TRIA_DOWN' if props.disp_mark_edge else 'TRIA_RIGHT',
            emboss=False
        )
        row.label(text="Mark Edge:")

        if props.disp_mark_edge:
            col = layout.column(align=True)

            row = col.row(align=True)
            row.operator('mesh.mark_sharp', text="Sharp", icon='X').clear = True
            row.operator('mesh.mark_sharp', text="Sharp", icon='IPO_CONSTANT')

            row = col.row(align=True)
            row.operator('mesh.mark_seam', text="Seam", icon='X').clear = True
            row.operator('mesh.mark_seam', text="Seam", icon='IPO_CIRC')

        # Shading
        row = layout.row(align=True)
        row.prop(
            props,
            'disp_shading',
            text="",
            icon='TRIA_DOWN' if props.disp_shading else 'TRIA_RIGHT',
            emboss=False
        )
        row.label(text="Shading:")

        if props.disp_shading:
            col = layout.column(align=True)
            col.operator('object.wire_all', icon='MESH_UVSPHERE')

            row = col.row(align=True)
            row.operator('mesh.set_smooth', text="Flat", icon='MESH_ICOSPHERE').clear = True
            row.operator('mesh.set_smooth', text="Smooth", icon='MATSPHERE')
            
            row = col.row(align=True)
            row.prop(shading,'light')
        
        
        row = layout.row(align=True)
        row.label(text="Display:")
        # Properties
        split = layout.split()
        col = split.column()
        #col.prop(obj.data, 'show_edge_sharp', text="Sharp")
        col.prop(overlay, 'show_edge_sharp', text="Sharp")
        #col.prop(obj.data, 'show_edge_seams', text="Seam")
        col.prop(overlay, 'show_edge_seams', text="Seam")

        col.prop(obj, 'show_in_front', text="In Front")
        #col.prop(obj, 'show_name', text="Name")
        
        col = split.column()
        #col.prop(obj.data, 'show_edge_crease', text="Crease")
        col.prop(overlay, 'show_edge_crease', text="Crease")
        col.prop(obj.data, 'use_mirror_x')

        col.prop(shading, 'show_backface_culling')


#----------------------------------------------------


def get_addon_prefs():
    return bpy.context.preferences.addons[__name__].preferences


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator('uv.cylinder_projection_ex')


# Store keymaps here to access after registration
addon_idname = [['mode.set_vertex', 'ONE'],
                ['mode.set_edge', 'TWO'],
                ['mode.set_face', 'THREE'],
                ['mode.toggle_occlude', 'FOUR'],
                ['mesh.dummy_function', 'FIVE'],
                ['mesh.dummy_function', 'SIX'],
                ['mesh.dummy_function', 'SEVEN'],
                ['mesh.dummy_function', 'EIGHT'],
                ['mesh.dummy_function', 'NINE'],
                ['mesh.dummy_function', 'ZERO']]
addon_keymaps = []


#-----------------------------------
# Registration
#-----------------------------------
classes = (
    LowpolyTools_Properties,
    LowpolyToolsPrefs,
    LPT_PT_LowpolyToolsEdit,
    LPT_PT_LowpolyToolsObject,
    LPT_OT_ToggleOcclude,
    LPT_OT_DummyFunction,
    LPT_OT_MeshSetOrigin,
    LPT_OT_CylinderProjectionEx,
    LPT_OT_SetFace,
    LPT_OT_SetEdge,
    LPT_OT_SetVertex,
    LPT_OT_FaceRotate,
    LPT_OT_ToggleMergeVertices,
    LPT_OT_SetSmooth,
    LPT_OT_SymmetrySnapX,
    LPT_OT_SymmetrizeMerge,
    LPT_OT_alignz,
    LPT_OT_aligny,
    LPT_OT_alignx,
    LPT_OT_Wire_All,
    LPT_OT_LapRelax,
    LPT_OT_Keybinding
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_uv_map.append(menu_func)
    bpy.app.translations.register(__name__, translation_dict)

    # Handle the keymap
    wm = bpy.context.window_manager

    #km = wm.keyconfigs.addon.keymaps.new(name="Mesh")
    #for idname, key in addon_idname:
    #    kmi = km.keymap_items.new(idname, key, 'PRESS')
    #    addon_keymaps.append((km, kmi))


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_uv_map.remove(menu_func)
    bpy.app.translations.unregister(__name__)

    # Handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    # Clear the list
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
