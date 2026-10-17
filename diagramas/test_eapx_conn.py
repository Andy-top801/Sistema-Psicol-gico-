import win32com.client
import uuid
import os

eap_path = os.path.abspath(r"diagramas\DIAGRAMAS.eapx")
conn = win32com.client.Dispatch('ADODB.Connection')
conn.Open(f'Provider=Microsoft.ACE.OLEDB.16.0;Data Source={eap_path};')

def guid():
    return '{' + str(uuid.uuid4()).upper() + '}'

# Test querying max IDs to verify connection
for tbl, col in [('t_package', 'Package_ID'), ('t_object', 'Object_ID'), ('t_diagram', 'Diagram_ID'), ('t_connector', 'Connector_ID')]:
    rs, _ = conn.Execute(f"SELECT MAX({col}) FROM {tbl}")
    print(f"Max {tbl}.{col} = {rs.Fields(0).Value}")

conn.Close()
print("Connection test successful!")
