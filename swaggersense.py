# Swagger_Analyzer_OpenRouter.py

import warnings
warnings.filterwarnings('ignore')

import os
import streamlit as st
import requests
import yaml

# Load OpenRouter API key from environment
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    st.error("❌ OPENROUTER_API_KEY not set in environment.")
    raise Exception("OPENROUTER_API_KEY not found.")

# ✅ Verify OpenRouter API Key
def verify_openrouter_auth():
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Title": "SwaggerAnalyzer"
        }
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        if response.status_code == 200:
            models = response.json().get("data", [])
            st.session_state['openrouter_models'] = len(models)
            st.success(f"✅ OpenRouter authentication successful! {len(models)} models available.")
            print("OpenRouter authentication successful!")
        else:
            st.error(f"❌ OpenRouter auth failed: {response.status_code} - {response.text}")
            raise Exception("OpenRouter API key invalid or expired.")
    except Exception as e:
        st.error(f"Error verifying OpenRouter key: {str(e)}")
        raise

# Run verification before doing anything else
verify_openrouter_auth()

# Define OpenRouter model (change if free models blocked)
openrouter_model_id = "meta-llama/llama-3.3-70b-instruct:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# 🔑 Function to call OpenRouter
def call_openrouter(prompt: str, system_role: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": openrouter_model_id,
        "messages": [
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"OpenRouter Error: {response.text}")

# --- Streamlit UI ---
def run_swagger_analyzer():
    st.title("📑 Swagger API Documentation Generator (OpenRouter)")

    swagger_file = st.file_uploader("Upload base Swagger YAML", type=["yaml", "yml"])
    reqres_file = st.file_uploader("Upload Request/Response text", type=["txt"])

    if swagger_file and reqres_file:
        swagger_base = yaml.safe_load(swagger_file.read())
        reqres_text = reqres_file.read().decode("utf-8")

        st.subheader("Base Swagger File")
        st.write(swagger_base)

        st.subheader("Request & Response")
        st.code(reqres_text, language="text")

        if st.button("Generate API Documentation", type="primary"):
            with st.spinner("Generating Swagger API Documentation..."):
                prompt = f"""
                You are an expert in OpenAPI/Swagger documentation.
                Given the base Swagger YAML and request/response details,
                expand it into a complete OpenAPI-compliant YAML.

                ---BASE SWAGGER---
                {yaml.dump(swagger_base)}

                ---REQUEST RESPONSE---
                {reqres_text}
                """
                try:
                    result = call_openrouter(prompt, "You are a Swagger/OpenAPI documentation expert.")
                    st.success("✅ Swagger Documentation Generated")

                    st.subheader("📑 Generated Swagger YAML")
                    st.code(result, language="yaml")

                    st.download_button(
                        label="Download Swagger YAML",
                        data=result,
                        file_name="swagger_generated.yaml",
                        mime="text/yaml"
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Run app
if __name__ == "__main__":
    run_swagger_analyzer()
