bl_info = {
		"name": "Export to AVS/UCD.ASCII (.inp)",
		"author": "Florian Sonner",
		"version": (1, 0),
		"blender": (2, 7, 4),
		"location": "File > Export > AVS/UCD.ASCII (.inp)",
		"description": "Export 2d polygonials to AVS/UCD file format (ASCII variant) and assigns colors to edges. Ignores z coordinates.",
		"warning": "",
		"wiki_url": "...",
		"tracker_url": "...dev..",
		"category": "Import-Export"}

import mathutils, math, struct
import bpy
from bpy.props import *
from os import remove
import time
from bpy_extras.io_utils import ExportHelper


def do_export(context, exporter, props, filepath):
		mesh = None
		
		for selected_object in bpy.context.selected_objects:
			if selected_object.type.lower() == 'mesh':
				if mesh != None:
					exporter.report({'ERROR'}, "More than one mesh selected. Aborting export.")
					return False
				else:
					mesh = selected_object
		
		if mesh == None:
			exporter.report({'ERROR'}, "No mesh selected in 'Object Mode'. Aborting export.")
			return False
		
		out = open(filepath, "w")
		
		vertices = mesh.data.vertices
		quads = mesh.data.polygons;
		
		'''
		First line of the .inp file requires us to know the number of boundary edges. As a
		3d program blender has no such concept, so we need to determine boundary edge on our 
		own. We do this by counting the number of adjacent quads for each edge:
			1 = boundary
			2 = inner
			3 = invalid mesh (3D)
		'''
		
		edge_numadj = { } # maps (v1, v2) to number of adjacent quads [v1 < v2 guaranteed for uniqueness]
		
		for idx, quad in enumerate(quads):
			for i in range(0, 4):
				v1idx = quad.vertices[i]
				v2idx = quad.vertices[(i + 1) % 4]
				
				edge_key = (min(v1idx, v2idx), max(v1idx, v2idx))
				
				if edge_key not in edge_numadj:
					edge_numadj[edge_key] = 1
				else:
					edge_numadj[edge_key] += 1
		
		boundary_edges = [ ]
		
		for edge_key, count in edge_numadj.items():
			if count == 1:
				boundary_edges.append(edge_key)
				
			elif count > 2:
				exporter.report({'ERROR'}, "Invalid mesh: One edge has more than two neighboring cells. Aborting export.")
				return False
			
		
		boundary_edge_colors = [ ]
		
		for edge in boundary_edges:
			v1 = edge[0]
			v2 = edge[1]
			
			v1_groups = [ ]
			v2_groups = [ ]
			
			for group in vertices[v1].groups:
				v1_groups.append(group.group)
				
			for group in vertices[v2].groups:
				v2_groups.append(group.group)
			
			common_groups = list(set(v1_groups) & set(v2_groups))
			
			if len(common_groups) > 1:
				exporter.report({'ERROR'}, "Invalid mesh: Edge vertices belong to more than one group. Aborting export.")
				return False
			
			if len(common_groups) == 1:
				boundary_edge_colors.append(common_groups[0]+1) # offset group idx by 1, zero are unassigned edges
			else:
				boundary_edge_colors.append(0)
		
		
		'''
		Begin output
		'''
		
		out.write('{numVertices} {numElements} 0 0 0\n'.format(numVertices = len(vertices), numElements = len(boundary_edges) + len(quads)))
		
		# print vertices
		for idx, v in enumerate(vertices):
			out.write('{idx} {x} {y} 0\n'.format(idx = idx, x = v.co[0], y = v.co[1]))
		
		# print quads and make vertices clockwise
		for idx, quad in enumerate(quads):
			# sum over edges to test if vertices are clockwise (see http://stackoverflow.com/a/1165943)
			clockwise_sum = 0
			
			for i in range(0, 4):
				# sum for clockwise test
				v1idx = quad.vertices[i]
				v1 = vertices[v1idx]
				v2idx = quad.vertices[(i + 1) % 4]
				v2 = vertices[v2idx]
				
				x1 = v1.co[0]
				y1 = v1.co[1]
				
				x2 = v2.co[0]
				y2 = v2.co[1]
				
				clockwise_sum += (x2 - x1) * (y2 + y1)
			
			if clockwise_sum < 0: # counterclockwise: order ok
				v0idx = quad.vertices[0]
				v1idx = quad.vertices[1]
				v2idx = quad.vertices[2]
				v3idx = quad.vertices[3]
			else: # clockwise: reverse order
				v0idx = quad.vertices[3]
				v1idx = quad.vertices[2]
				v2idx = quad.vertices[1]
				v3idx = quad.vertices[0]
			
		
			out.write('{idx} 0 quad {v0} {v1} {v2} {v3}\n'.format(idx = idx, v0 = v0idx, v1 = v1idx, v2 = v2idx, v3 = v3idx))
		
		# print boundary edges
		for idx, edge in enumerate(boundary_edges):
			out.write('{idx} {col} line {v0} {v1}\n'.format(idx = idx, col = boundary_edge_colors[idx], v0 = edge[0], v1 = edge[1]))
		
		out.flush()
		out.close()
		return True


class Export_ucd(bpy.types.Operator, ExportHelper):
		bl_idname = "export_shape.ucd"
		bl_label = "Export AVS/UCD.ASCII (.inp)"
		filename_ext = ".inp"
		

		
		@classmethod
		def poll(cls, context):
				return context.active_object.type in {'MESH'}

		def execute(self, context):
				start_time = time.time()
				print('\n_____START_____')
				props = self.properties
				filepath = self.filepath
				filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

				exported = do_export(context, self, props, filepath)
				
				if exported:
						print('finished export in %s seconds' %((time.time() - start_time)))
						print(filepath)
						
				return {'FINISHED'}

		def invoke(self, context, event):
				wm = context.window_manager

				if True:
						# File selector
						wm.fileselect_add(self) # will run self.execute()
						return {'RUNNING_MODAL'}
				elif True:
						# search the enum
						wm.invoke_search_popup(self)
						return {'RUNNING_MODAL'}
				elif False:
						# Redo popup
						return wm.invoke_props_popup(self, event)
				elif False:
						return self.execute(context)


def menu_func(self, context):
		self.layout.operator(Export_ucd.bl_idname, text="AVS/UCD.ASCII (.inp)")

def register():
		bpy.utils.register_module(__name__)
		bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
		bpy.utils.unregister_module(__name__)
		bpy.types.INFO_MT_file_export.remove(menu_func)
		
if __name__ == "__main__":
		register()
