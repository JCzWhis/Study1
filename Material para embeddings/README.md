# Material para Embeddings

Coloca aquí los documentos que quieres procesar:

## Formatos soportados:
- PDF (.pdf)
- HTML (.html, .htm) - Exports de Notion
- Markdown (.md)
- CSV (.csv)
- Word (.docx)
- Excel (.xlsx, .xls)
- Texto plano (.txt)

## Recomendaciones:
- Archivos individuales < 50MB
- Total recomendado: 250MB - 1GB
- Contenido en español/inglés
- Nombres de archivo sin caracteres especiales

## Estructura recomendada:
```
Material para embeddings/
├── medicina_interna/
│   ├── cardiologia/
│   ├── endocrinologia/
│   └── ...
├── documentos_generales/
└── papers_investigacion/
```

Una vez que hayas colocado tus documentos, ejecuta:
```bash
python embeddings_processor.py
```
