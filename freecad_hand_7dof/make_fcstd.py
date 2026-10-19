"""Generate a native FreeCAD .FCStd file WITHOUT FreeCAD installed.
FCStd = ZIP containing Document.xml + Part shapes as .brep + GuiDocument.xml.
Shapes here are mesh-based (Mesh::MeshObject) referencing the STL geometry
as triangle facets, so FreeCAD opens it directly with visible parts.
"""
import os, zipfile, struct
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
MESH = os.path.join(HERE, "meshes")
OUT = os.path.join(HERE, "hand_7dof.FCStd")

def read_stl_tris(path):
    with open(path, "rb") as fh:
        data = fh.read()
    n = struct.unpack("<I", data[80:84])[0]
    tris = []
    off = 84
    for _ in range(n):
        vals = struct.unpack("<12fH", data[off:off+50])
        tris.append(vals[3:12])
        off += 50
    return np.array(tris, float).reshape(-1, 3)

parts = sorted(f for f in os.listdir(MESH) if f.endswith(".stl"))
doc_objs, gui_objs = [], []
for i, f in enumerate(parts):
    name = os.path.splitext(f)[0]
    tris = read_stl_tris(os.path.join(MESH, f))  # (N,3)
    flat = tris
    ntri = len(flat) // 3
    pts = "\n".join(
        f"      <P X=\"{p[0]:.6f}\" Y=\"{p[1]:.6f}\" Z=\"{p[2]:.6f}\"/>"
        for p in flat)
    facets = []
    for k in range(ntri):
        a, b, c = 3*k, 3*k+1, 3*k+2
        facets.append(f"      <F I0=\"{a}\" I1=\"{b}\" I2=\"{c}\" N0=\"{a}\" N1=\"{b}\" N2=\"{c}\"/>")
    doc_objs.append(f"""    <Object name="{name}" type="Mesh::Feature">
      <Properties>
        <Property name="Mesh" type="Mesh::PropertyMeshKernel">
          <Mesh>
            <Points Count="{len(flat)}">
{pts}
            </Points>
            <Facets Count="{ntri}">
{chr(10).join(facets)}
            </Facets>
          </Mesh>
        </Property>
        <Property name="Label" type="App::PropertyString"><String value="{name}"/></Property>
      </Properties>
    </Object>""")
    c = (0.55+0.08*(i%3), 0.6, 0.75-0.07*i, 0.0)
    gui_objs.append(f"""    <ViewProvider name="{name}" type="MeshGui::ViewProviderMesh">
      <Properties>
        <Property name="ShapeColor" type="App::PropertyColor"><PropertyColor R="{c[0]:.2f}" G="{c[1]:.2f}" B="{c[2]:.2f}" A="{c[3]:.2f}"/></Property>
      </Properties>
    </ViewProvider>""")

document_xml = f"""<?xml version='1.0' encoding='utf-8'?>
<Document SchemaVersion="4" ProgramVersion="1.0" FileVersion="1">
  <Properties>
    <Property name="Comment" type="App::PropertyString"><String value="7-DOF hand: Fetch 2-finger gripper + 5 wrist/palm DOF"/></Property>
    <Property name="Label" type="App::PropertyString"><String value="Hand7DOF"/></Property>
  </Properties>
  <Objects Count="{len(parts)}">
{chr(10).join(doc_objs)}
  </Objects>
</Document>
"""
gui_xml = f"""<?xml version='1.0' encoding='utf-8'?>
<GuiDocument SchemaVersion="1">
  <ViewProviders Count="{len(parts)}">
{chr(10).join(gui_objs)}
  </ViewProviders>
</GuiDocument>
"""
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("Document.xml", document_xml)
    z.writestr("GuiDocument.xml", gui_xml)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
