import win32com.client
import os

eap_path = os.path.abspath(r"diagramas\DIAGRAMAS.eapx")
conn = win32com.client.Dispatch('ADODB.Connection')
conn.Open(f'Provider=Microsoft.ACE.OLEDB.16.0;Data Source={eap_path};')

rs, _ = conn.Execute('SELECT Package_ID, Name FROM t_package WHERE Parent_ID = 89 ORDER BY Package_ID')
while not rs.EOF:
    pid = rs.Fields(0).Value
    name = rs.Fields(1).Value
    rs_d, _ = conn.Execute(f'SELECT Diagram_ID, Name, Diagram_Type FROM t_diagram WHERE Package_ID = {pid}')
    diags = []
    while not rs_d.EOF:
        diags.append((rs_d.Fields(0).Value, rs_d.Fields(1).Value, rs_d.Fields(2).Value))
        rs_d.MoveNext()
    diag_str = ', '.join([f'Diag [{did}] \"{dname}\" ({dtype})' for did, dname, dtype in diags])
    print(f'Pkg [{pid}] \"{name}\"' + (f' -> {diag_str}' if diags else ''))
    rs.MoveNext()
