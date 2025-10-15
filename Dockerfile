# Imagen base oficial de Python
FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY ./app /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

