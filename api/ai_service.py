from openai import OpenAI
from django.db import connection
import json

# Configuración del cliente OpenRouter
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

def ask_sql_assistant(question):
    # Definición del esquema simplificado para el contexto del LLM
    schema_context = """
    Tablas disponibles:
    1. api_proveedor (columnas: id, nombre, direccion, telefono, correo)
    2. api_llaves (columnas: id, cod_llave, cantidad, img, proveedor_id) (relacion: proveedor_id -> api_proveedor.id)
    
    Solo devuelve la consulta SQL cruda, sin markdown ni explicaciones adicionales. La consulta debe ser compatible con SQLite.
    Ejemplo: SELECT * FROM api_llaves LIMIT 5;
    """

    try:
        completion = client.chat.completions.create(
            model="mistralai/mistral-tiny",
            messages=[
                {
                    "role": "system",
                    "content": f"Eres un experto en SQL y bases de datos. Tu trabajo es convertir preguntas en lenguaje natural a consultas SQL seguras (solo SELECT). {schema_context}"
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        
        sql_query = completion.choices[0].message.content.strip()
        
        # Limpieza básica por seguridad (muy simple)
        if "```sql" in sql_query:
            sql_query = sql_query.replace("```sql", "").replace("```", "")
        
        if not sql_query.upper().startswith("SELECT"):
            return {"error": "Solo se permiten consultas de lectura (SELECT)."}

        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            results = [dict(zip(columns, row)) for row in rows]
            
        return {
            "query": sql_query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        return {"error": str(e)}
