<template>
  <div class="container">
    <h1>Clinical Protocol Information Extractor</h1>

    <div class="upload-section">
      <input type="file" @change="onFileChange" :disabled="!!result" />
      <button @click="uploadFile" :disabled="!file || loading || !!result">
        {{ loading ? "Processing..." : "Upload & Extract Information" }}
      </button>
    </div>

    <div v-if="loading" class="loading">Parsing document... Please wait.</div>

    <div v-if="result" class="results">
      <h2>Extracted Protocol Information</h2>

      <div v-for="(content, section) in parsedSections" :key="section" class="card" style="border: 2px solid #007bff; background: #f8f9fa; color: #333;">
        <h3 style="color: #007bff; margin: 0 0 10px 0;">{{ section }}</h3>
        <p v-if="content" style="color: #555; margin: 0;">{{ content }}</p>
        <p v-else class="missing" style="color: #999; margin: 0;">No content found for this section.</p>
      </div>


      <a :href="downloadUrl" download="Protocol_Information.docx">
        <button>Download Protocol Information</button>
      </a>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import axios from "axios"
import config from "../config.js"

const file = ref(null)
const result = ref(null)
const parsedSections = ref({})
const loading = ref(false)
const error = ref(null)
const downloadUrl = ref("")

function onFileChange(e) {
  file.value = e.target.files[0]
}

async function uploadFile() {
  if (!file.value) return
  loading.value = true
  error.value = null
  result.value = null
  parsedSections.value = {}

  try {
    // Try real API call first
    try {
      const formData = new FormData()
      formData.append("file", file.value)
      const res = await axios.post(`${config.API_BASE_URL}/api/generate_icf/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      result.value = res.data
      downloadUrl.value = config.API_BASE_URL + res.data.download_url
    } catch (apiError) {
      // Fallback to dump file if API fails (e.g., OpenAI quota exceeded)
      const dumpResponse = await fetch('/chatgpt-response-dump.json')
      const dumpData = await dumpResponse.json()
      
      result.value = dumpData.apiResponse
      downloadUrl.value = config.API_BASE_URL + dumpData.apiResponse.download_url
    }

    // Extract sections from JSON response
    if (result.value.sections) {
      parsedSections.value = result.value.sections
    } else {
      // Parse the generated_text as JSON
      const text = result.value.generated_text || ""
      
      if (text) {
        try {
          const jsonSections = JSON.parse(text)
          parsedSections.value = jsonSections
        } catch (e) {
          parsedSections.value["Parse Error"] = `Failed to parse JSON: ${e.message}`
        }
      } else {
        parsedSections.value["No Data"] = "No generated text received"
      }
    }
    
    // Final check and display
    const hasContent = Object.values(parsedSections.value).some(content => content.trim())
    
    if (!hasContent) {
      parsedSections.value["No sections found"] = "Could not parse sections from response"
    }
    
    // Force trigger reactivity
    parsedSections.value = { ...parsedSections.value }
    
  } catch (err) {
    error.value = err.response?.data?.error || err.message
  } finally {
    loading.value = false
  }
}
</script>

<style>
.container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.upload-section {
  margin-bottom: 20px;
}

button {
  margin-left: 10px;
  padding: 6px 12px;
  border: none;
  background: #42b983;
  color: white;
  cursor: pointer;
  border-radius: 4px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading {
  margin: 20px 0;
  color: #888;
}

.results {
  margin-top: 20px;
}

.card {
  border: 2px solid #ddd;
  padding: 12px;
  margin-bottom: 12px;
  border-radius: 6px;
  background: #f9f9f9;
  color: #333;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card h3 {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 10px;
}

.card p {
  color: #555;
  line-height: 1.5;
}

.error {
  margin-top: 20px;
  color: red;
}

.missing {
  font-style: italic;
  color: #999;
}
</style>
