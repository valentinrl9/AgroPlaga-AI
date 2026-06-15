import zipfile, os
path = r'c:\Proyecto PlagaIA\Guia del proyecto.odt'
print('exists', os.path.exists(path))
with zipfile.ZipFile(path, 'r') as z:
    print('names', [n for n in z.namelist() if n in ('content.xml','styles.xml','meta.xml') or n.endswith('.xml')])
    content = z.read('content.xml').decode('utf-8', errors='ignore')
    print(content[:8000])
