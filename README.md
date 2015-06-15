
# Blender 2D UCD Export Script

This script can be used to export two-dimensional meshes from blender into the `ucd` file format (file extension `.inp`), a file format used in some scientific communities for mesh geometries. Both vertex data and quads are exported, but just boundary lines of the mesh. After installation the mesh can be exported through the usual `File -> Export` menu. For this the mesh with the geometry must be selected in `Object Mode`.

**Installation.**
Go to `File -> User Preferences -> Add-ons`, click `Install from File..` and choose the `exportucd.py` file. Then enable the add-on by checking the checkbox on the right. 

**Boundary Edge Coloring.** Coloring of boundary edges is supported by assigning both edge vertices to the same *vertex group* in blender. The color/material id of the boundary line is determined through the internal group index. If no vertex group is assigned the edge color will be `0`.

**Notes.**
 * The `z` coordinate is ignored during export.
 * The mesh must be planar in the sense that each edge can have at most two adjacent quads.
 * The vertices of quads are ordered counter-clockwise because some libraries expect this.
 * At export exactly one mesh must be selected in the `Object Mode`. (Note that the mesh can be changed in `Edit Mode` even if it is not selected in `Object Mode`.)
 * The export is performed in the `ASCII` variant of the `ucd` format.
