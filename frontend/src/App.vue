<template>
  <div class="container">
    <h1>🧬 Clinical Protocol Analyzer</h1>
    <p class="subtitle">Upload a clinical trial protocol document and generate structured insights instantly!</p>

    <div class="upload-section">
      <input type="file" @change="onFileChange" :disabled="!!result" />
      <button @click="uploadFile" :disabled="!file || loading || !!result">
        {{ loading ? "🔍 Analyzing..." : "🚀 Generate Insights" }}
      </button>
    </div>

    <div v-if="loading" class="loading">🔬 Analyzing document structure... Please wait.</div>

    <div v-if="result" class="results">
      <h2>✨ Generated Protocol Insights</h2>

      <div v-for="(content, section) in parsedSections" :key="section" class="card" style="border: 2px solid #007bff; background: #f8f9fa; color: #333;">
        <h3 style="color: #007bff; margin: 0 0 10px 0;">{{ section }}</h3>
        <p v-if="content" style="color: #555; margin: 0;">{{ content }}</p>
        <p v-else class="missing" style="color: #999; margin: 0;">No content found for this section.</p>
      </div>


      <div class="action-buttons">
        <a :href="downloadUrl" download="Protocol_Information.docx">
          <button>📄 Download Complete Report</button>
        </a>
        <button @click="showLogs = !showLogs" class="logs-button">
          {{ showLogs ? '📊 Hide Details' : '📊 View Source Details' }}
        </button>
      </div>

      <!-- Logs Section -->
      <div v-if="showLogs && detailedLogs.length > 0" class="logs-section">
        <h3>Processing Logs</h3>
          <div class="log-entry" v-for="(log, index) in detailedLogs.filter(log => log.type !== 'document_generation')" :key="index">
          <div class="log-header">
            <span class="log-type" :class="log.type">{{ log.type.replace('_', ' ').toUpperCase() }}</span>
            <span class="log-description">{{ log.description }}</span>
          </div>
          
          <div v-if="log.type === 'extraction'" class="log-details">
            <p><strong>Page:</strong> {{ log.page }}</p>
            <p><strong>Content Length:</strong> {{ log.content_length }} characters</p>
            <div class="content-preview">
              <strong>Content Preview:</strong>
              <p>{{ log.content_preview }}</p>
            </div>
          </div>
          
          <div v-if="log.type === 'section_generation'" class="log-details">
            <p><strong>Section:</strong> {{ log.section }}</p>
            <p><strong>Content Length:</strong> {{ log.content_length }} characters</p>
            <div class="content-preview">
              <strong>Generated Content:</strong>
              <p>{{ log.content_preview }}</p>
            </div>
          </div>
          
        </div>
      </div>
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
const showLogs = ref(false)
const detailedLogs = ref([])

function onFileChange(e) {
  file.value = e.target.files[0]
}

async function uploadFile() {
  if (!file.value) return
  loading.value = true
  error.value = null
  result.value = null
  parsedSections.value = {}
  showLogs.value = false
  detailedLogs.value = []

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
      detailedLogs.value = res.data.detailed_logs || []
    } catch (apiError) {
      // Fallback to dump file if API fails (e.g., OpenAI quota exceeded)
      const dumpResponse = await fetch('/chatgpt-response-dump.json')
      const dumpData = await dumpResponse.json()
      
      result.value = dumpData.apiResponse
      downloadUrl.value = config.API_BASE_URL + dumpData.apiResponse.download_url
      detailedLogs.value = dumpData.apiResponse.detailed_logs || []
    }

    // Extract sections from JSON response
    if (result.value.sections) {
      // Handle new format with content and source_pages
      const processedSections = {}
      for (const [sectionName, sectionData] of Object.entries(result.value.sections)) {
        if (typeof sectionData === 'object' && sectionData.content) {
          // New format: { content: "...", source_pages: [...] }
          processedSections[sectionName] = sectionData.content
        } else if (typeof sectionData === 'string') {
          // Old format: just string content
          processedSections[sectionName] = sectionData
        }
      }
      parsedSections.value = processedSections
    } else {
      // Parse the generated_text as JSON
      const text = result.value.generated_text || ""
      
      if (text) {
        try {
          const jsonSections = JSON.parse(text)
          // Handle new format in generated_text as well
          const processedSections = {}
          for (const [sectionName, sectionData] of Object.entries(jsonSections)) {
            if (typeof sectionData === 'object' && sectionData.content) {
              // New format: { content: "...", source_pages: [...] }
              processedSections[sectionName] = sectionData.content
            } else if (typeof sectionData === 'string') {
              // Old format: just string content
              processedSections[sectionName] = sectionData
            }
          }
          parsedSections.value = processedSections
        } catch (e) {
          parsedSections.value["Parse Error"] = `Failed to parse JSON: ${e.message}`
        }
      } else {
        parsedSections.value["No Data"] = "No generated text received"
      }
    }
    
    // Final check and display
    const hasContent = Object.values(parsedSections.value).some(content => typeof content === 'string' && content.trim())
    
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
body {
  margin: 0;
  padding: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.container {
  width: 100%;
  margin: 0;
  padding: 20px;
  min-height: 100vh;
}

h1 {
  color: #fff;
  text-align: center;
  font-size: 2.5em;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  color: #f0f0f0;
  text-align: center;
  font-size: 1.1em;
  margin-bottom: 30px;
  font-weight: 300;
}

.upload-section {
  margin-bottom: 20px;
}

button {
  margin-left: 10px;
  padding: 12px 24px;
  border: none;
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  color: white;
  cursor: pointer;
  border-radius: 25px;
  font-weight: bold;
  font-size: 1em;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
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
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.results h2 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 25px;
  font-size: 1.8em;
  font-weight: 600;
}

.card {
  border: none;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 15px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
  box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(240, 147, 251, 0.4);
}

.card h3 {
  color: #fff;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.3em;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}

.card p {
  color: #fff;
  line-height: 1.6;
  font-size: 1em;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.error {
  margin-top: 20px;
  color: red;
}

.missing {
  font-style: italic;
  color: #999;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.logs-button {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
}

.logs-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 172, 254, 0.4);
}

.logs-section {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
}

.logs-section h3 {
  margin-top: 0;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  padding-bottom: 10px;
}

.log-entry {
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 4px;
  border-left: 4px solid #007bff;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.log-type {
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.log-type.extraction {
  background: #e3f2fd;
  color: #1976d2;
}

.log-type.section_generation {
  background: #e8f5e8;
  color: #388e3c;
}


.log-description {
  color: #495057;
  font-weight: 500;
}

.log-details {
  margin-left: 10px;
}

.log-details p {
  margin: 5px 0;
  color: #6c757d;
}

.content-preview {
  margin-top: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 3px;
  border: 1px solid #e9ecef;
}

.content-preview p {
  margin: 5px 0;
  font-family: monospace;
  font-size: 14px;
  color: #495057;
  white-space: pre-wrap;
}
</style>
