import win32com.client
import os

eap_path = os.path.abspath(r"diagramas\DIAGRAMAS.eapx")
conn = win32com.client.Dispatch('ADODB.Connection')
conn.Open(f'Provider=Microsoft.ACE.OLEDB.16.0;Data Source={eap_path};')

def inspect_diagram(diag_id):
    rs, _ = conn.Execute(f"SELECT Diagram_ID, Name, Diagram_Type, Package_ID, StyleEx FROM t_diagram WHERE Diagram_ID = {diag_id}")
    if rs.EOF:
        print("Diagram not found:", diag_id)
        return
    print(f"\n=== Diagram [{rs.Fields(0).Value}] \"{rs.Fields(1).Value}\" ({rs.Fields(2).Value}) ===")
    
    # Diagram Objects
    rs_obj, _ = conn.Execute(f"SELECT do.Instance_ID, do.Object_ID, o.Name, o.Object_Type, o.Stereotype, do.RectTop, do.RectLeft, do.RectRight, do.RectBottom FROM t_diagramobjects do INNER JOIN t_object o ON do.Object_ID = o.Object_ID WHERE do.Diagram_ID = {diag_id}")
    print("  Objects on diagram:")
    while not rs_obj.EOF:
        print(f"    - Obj [{rs_obj.Fields(1).Value}] \"{rs_obj.Fields(2).Value}\" ({rs_obj.Fields(3).Value}, St: {rs_obj.Fields(4).Value}) at ({rs_obj.Fields(5).Value}, {rs_obj.Fields(6).Value}, {rs_obj.Fields(7).Value}, {rs_obj.Fields(8).Value})")
        rs_obj.MoveNext()
        
    # Diagram Connectors
    sql_conn = f"""
    SELECT dl.ConnectorID, c.Connector_Type, c.Name, o1.Name, o2.Name 
    FROM ((t_diagramlinks dl 
           INNER JOIN t_connector c ON dl.ConnectorID = c.Connector_ID) 
           INNER JOIN t_object o1 ON c.Start_Object_ID = o1.Object_ID) 
           INNER JOIN t_object o2 ON c.End_Object_ID = o2.Object_ID 
    WHERE dl.DiagramID = {diag_id}
    """
    rs_conn, _ = conn.Execute(sql_conn)
    print("  Connectors on diagram:")
    while not rs_conn.EOF:
        print(f"    - Conn [{rs_conn.Fields(0).Value}] \"{rs_conn.Fields(2).Value}\" ({rs_conn.Fields(1).Value}): \"{rs_conn.Fields(3).Value}\" -> \"{rs_conn.Fields(4).Value}\"")
        rs_conn.MoveNext()

for did in [75, 76, 100, 151, 96, 137, 213]:
    inspect_diagram(did)
