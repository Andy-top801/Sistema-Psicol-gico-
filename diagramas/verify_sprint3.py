import win32com.client
import sys

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

conn = win32com.client.Dispatch('ADODB.Connection')
conn.Open(r'Provider=Microsoft.ACE.OLEDB.16.0;Data Source=diagramas\DIAGRAMAS.eapx;')

print("================================================================================")
print("             VERIFICACIÓN DE MODELADO SPRINT 3 EN DIAGRAMAS.EAPX                ")
print("================================================================================")

rs_root, _ = conn.Execute("SELECT Package_ID, Name, ea_guid FROM t_package WHERE Parent_ID = 1 AND Name LIKE '%Sprint 3%'")
if rs_root.EOF:
    print("ERROR: No se encontró el paquete raíz del Sprint 3.")
    conn.Close()
    sys.exit(1)

root_id = rs_root.Fields(0).Value
root_name = rs_root.Fields(1).Value
print(f"\nPaquete Raíz: [{root_id}] '{root_name}'\n")

# Recursive package list
def print_tree(pid, indent=""):
    rs_sub, _ = conn.Execute(f"SELECT Package_ID, Name FROM t_package WHERE Parent_ID = {pid} ORDER BY Package_ID")
    while not rs_sub.EOF:
        sub_id = rs_sub.Fields(0).Value
        sub_name = rs_sub.Fields(1).Value
        rs_diag, _ = conn.Execute(f"SELECT Diagram_ID, Name, Diagram_Type FROM t_diagram WHERE Package_ID = {sub_id} ORDER BY Diagram_ID")
        diag_info = []
        while not rs_diag.EOF:
            diag_info.append(f"Diag [{rs_diag.Fields(0).Value}]: '{rs_diag.Fields(1).Value}' ({rs_diag.Fields(2).Value})")
            rs_diag.MoveNext()
        
        d_str = " | " + ", ".join(diag_info) if diag_info else ""
        print(f"{indent}• [{sub_id}] {sub_name}{d_str}")
        print_tree(sub_id, indent + "    ")
        rs_sub.MoveNext()

print("Estructura Jerárquica de Paquetes y Diagramas:")
print_tree(root_id, "  ")

# Statistics
rs_pkg_cnt, _ = conn.Execute(f"SELECT COUNT(*) FROM t_package WHERE Package_ID = {root_id} OR Parent_ID = {root_id} OR Parent_ID IN (SELECT Package_ID FROM t_package WHERE Parent_ID = {root_id})")
rs_diag_cnt, _ = conn.Execute(f"SELECT COUNT(*) FROM t_diagram WHERE Package_ID IN (SELECT Package_ID FROM t_package WHERE Package_ID = {root_id} OR Parent_ID = {root_id} OR Parent_ID IN (SELECT Package_ID FROM t_package WHERE Parent_ID = {root_id}))")
rs_obj_cnt, _ = conn.Execute(f"SELECT COUNT(*) FROM t_object WHERE Package_ID IN (SELECT Package_ID FROM t_package WHERE Package_ID = {root_id} OR Parent_ID = {root_id} OR Parent_ID IN (SELECT Package_ID FROM t_package WHERE Parent_ID = {root_id}))")
rs_conn_cnt, _ = conn.Execute(f"SELECT COUNT(*) FROM t_connector WHERE Start_Object_ID IN (SELECT Object_ID FROM t_object WHERE Package_ID IN (SELECT Package_ID FROM t_package WHERE Package_ID = {root_id} OR Parent_ID = {root_id} OR Parent_ID IN (SELECT Package_ID FROM t_package WHERE Parent_ID = {root_id})))")

print("\n--------------------------------------------------------------------------------")
print("RESUMEN DE ELEMENTOS INSERTADOS EN SPRINT 3:")
print(f"  • Total Paquetes Creados:    {rs_pkg_cnt.Fields(0).Value}")
print(f"  • Total Diagramas UML:       {rs_diag_cnt.Fields(0).Value}")
print(f"  • Total Objetos/Clases/Act:  {rs_obj_cnt.Fields(0).Value}")
print(f"  • Total Conectores/Mensajes: {rs_conn_cnt.Fields(0).Value}")
print("================================================================================")

conn.Close()
