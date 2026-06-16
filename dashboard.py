import asyncio
import os
from typing import Any, cast

import httpx
import streamlit as st

# Configuración
API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(page_title="Feed de Contenido Personal", page_icon="📰", layout="wide")

st.title("📰 Feed de Contenido Personal")
st.markdown("Genera informes de investigación temáticos usando agentes de LangGraph.")

with st.sidebar:
    st.header("Configuración")
    api_endpoint = st.text_input("URL de la API", value=API_URL)

    st.info("""
    Este panel interactúa con la API de Content Feed para explorar la web 
    y generar informes.
    """)

# Interfaz Principal
query_input = st.text_area(
    "Ingresa tus consultas de búsqueda (una por línea):",
    placeholder="ej.\nÚltimas noticias sobre SpaceX\nAvances en agentes de IA",
    height=150,
)


async def run_scout(queries: list[str]) -> dict[str, Any] | None:
    async with httpx.AsyncClient(timeout=300.0) as client:
        payload = {"query": queries, "findings": [], "iteration": 0, "critic_feedback": None, "final_report": None}
        try:
            response = await client.post(f"{api_endpoint}/scout", json=payload)
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except Exception as e:
            st.error(f"Error al conectar con la API: {e}")
            return None


if st.button("🚀 Explorar y Generar Informe", type="primary"):
    queries = [q.strip() for q in query_input.split("\n") if q.strip()]

    if not queries:
        st.warning("Por favor, ingresa al menos una consulta.")
    else:
        with st.spinner("🕵️ El agente está explorando la web... Esto puede tardar un minuto."):
            result = asyncio.run(run_scout(queries))

            if result:
                st.success("✅ ¡Informe Generado!")

                # Mostrar métricas
                latency = result.get("latency_breakdown", {}).get("ai_inference_sec", 0)
                st.caption(f"Latencia: {latency}s | ID de Hilo: {result.get('thread_id')}")

                # Mostrar Informe
                st.divider()
                st.markdown(result.get("agent_response", "No se devolvió contenido del informe."))

st.divider()
st.caption("Construido con Streamlit & LangGraph")
