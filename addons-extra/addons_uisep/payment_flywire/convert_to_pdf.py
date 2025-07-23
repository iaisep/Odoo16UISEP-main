import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import simpleSplit
from datetime import datetime

# Nombre del script a ignorar
SCRIPT_NAME = "convert_to_pdf.py"

# Registrar una fuente que soporte caracteres Unicode
pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))

# Extensiones permitidas
ALLOWED_EXTENSIONS = (".py", ".xml", ".js")

# Función para generar un árbol de archivos filtrando por extensiones permitidas
def generate_file_tree(path, prefix=""):
    file_tree = []
    contents = sorted(os.listdir(path))  # Ordenar alfabéticamente

    for index, name in enumerate(contents):
        full_path = os.path.join(path, name)
        connector = "└── " if index == len(contents) - 1 else "├── "

        if os.path.isdir(full_path):
            # Revisar si dentro de la carpeta hay archivos con extensiones permitidas
            sub_tree = generate_file_tree(full_path, prefix + "│   ")
            if sub_tree:  # Solo mostrar carpetas que contienen archivos permitidos
                file_tree.append(f"{prefix}{connector}[DIR] {name}")
                file_tree.extend(sub_tree)
        elif name.endswith(ALLOWED_EXTENSIONS):  # Solo incluir archivos permitidos
            file_tree.append(f"{prefix}{connector}{name}")

    return file_tree

# Ruta raíz del proyecto
project_path = os.getcwd()

# Obtener el nombre de la carpeta raíz
project_name = os.path.basename(project_path)

# Generar el árbol de archivos solo con archivos permitidos
file_tree = generate_file_tree(project_path)

# Detectar archivos a procesar con ruta relativa corregida
files_to_process = []
for root, _, files in os.walk(project_path):
    for file in sorted(files):
        if file == SCRIPT_NAME or not file.endswith(ALLOWED_EXTENSIONS):
            continue
        full_path = os.path.join(root, file)
        relative_path = os.path.relpath(full_path, project_path).replace("\\", "/")  # Normaliza las barras
        files_to_process.append((full_path, f"/{relative_path}"))  # Guardamos ruta absoluta y relativa corregida

# Verificar si hay archivos para procesar
if not files_to_process:
    print("⚠️ No se encontraron archivos .py, .xml o .js. No se generará el PDF.")
    exit(1)

# Nombre del archivo PDF final
fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S") 

pdf_file_name = os.path.join(project_path, "%s_%s.pdf" % (project_name,fecha_hora ) )

# Crear PDF
c = canvas.Canvas(pdf_file_name, pagesize=A4)
c.setTitle(project_name)
c.setFont("DejaVu", 10)  # Usar la fuente registrada

# Dimensiones de la hoja
width, height = A4
max_width = width - 100  # Espacio máximo para el texto antes de cortar

# Posición inicial
x_start, y_start = 50, height - 50

# Agregar título del proyecto
c.setFont("DejaVu", 16)
c.drawString(x_start, y_start, project_name)
y_start -= 20

# Agregar el árbol de archivos filtrado con fuente más pequeña
y_start -= 10
c.setFont("DejaVu", 8)  # Cambiar el tamaño de la fuente a 8
for line in file_tree:
    if y_start < 50:  # Salto de página si no hay espacio
        c.showPage()
        c.setFont("DejaVu", 8)  # Mantener el tamaño de la fuente en 8
        y_start = height - 50
    c.drawString(x_start, y_start, line)
    y_start -= 10  # Reducir el espacio entre líneas para el árbol

# Función para limpiar caracteres no imprimibles
def clean_text(text):
    text = text.replace("\t", "    ")  # Convertir tabulaciones a 4 espacios
    text = re.sub(r'[^\x20-\x7E\t\n]', '', text)  # Eliminar caracteres fuera del rango imprimible
    return text

# Función para dividir el texto conservando la indentación
def split_preserve_indent(text, font, font_size, max_width):
    lines = []
    for line in text.split("\n"):
        # Calcular la indentación de la línea actual
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]  # Conservar los espacios o tabulaciones

        # Dividir el texto sin la indentación
        wrapped_lines = simpleSplit(line[indent:], font, font_size, max_width)

        # Agregar la indentación a cada línea dividida
        for wrapped_line in wrapped_lines:
            lines.append(indent_str + wrapped_line)
    return lines

# Agregar archivos y su contenido con ajuste forzado de línea y conservando la indentación
y_start -= 20
for full_path, relative_path in files_to_process:
    if y_start < 50:
        c.showPage()
        y_start = height - 50

    # Añadir un salto de línea antes de la ruta del archivo
    y_start -= 12  # Salto de línea antes de --- /ruta/del/archivo ---

    c.setFont("DejaVu", 12)
    c.drawString(x_start, y_start, f"--- {relative_path} ---")  # Ruta relativa corregida en Unix
    y_start -= 15  # Espacio después de la ruta del archivo

    c.setFont("DejaVu", 8)

    with open(full_path, "r", encoding="utf-8") as infile:
        text = infile.read()
        text = clean_text(text)  # Limpiar el texto

        # Dividir el texto conservando la indentación
        wrapped_lines = split_preserve_indent(text, "DejaVu", 8, max_width)

        # Dibujar cada línea en el PDF
        for line in wrapped_lines:
            if y_start < 50:
                c.showPage()
                y_start = height - 50
                c.setFont("DejaVu", 8)
            c.drawString(x_start, y_start, line)
            y_start -= 12  # Ajustar la posición vertical después de cada línea

# Guardar el PDF
c.save()
print(f"✅ PDF generado correctamente: {pdf_file_name}")