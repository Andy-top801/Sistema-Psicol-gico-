import win32com.client
import os

eap_path = os.path.abspath(r"diagramas\DIAGRAMAS.eapx")
conn = win32com.client.Dispatch('ADODB.Connection')
conn.Open(f'Provider=Microsoft.ACE.OLEDB.16.0;Data Source={eap_path};')

rs, _ = conn.Execute("SELECT Package_ID, Name, Parent_ID FROM t_package WHERE Name LIKE '%Sprint 3%' OR Name LIKE '%sprint 3%'")
found = []
while not rs.EOF:
    found.append((rs.Fields(0).Value, rs.Fields(1).Value, rs.Fields(2).Value))
    rs.MoveNext()
print('Found Sprint 3 packages:', found)
