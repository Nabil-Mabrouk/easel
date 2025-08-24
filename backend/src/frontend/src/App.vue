<template>
  <div style="max-width:720px;margin:40px auto;font-family:system-ui;">
    <h1>KidsBookAI</h1>
    <form @submit.prevent="submit">
      <label>Painting ID</label>
      <select v-model="form.painting_id">
        <option value="starry_night">starry_night</option>
        <option value="mona_lisa">mona_lisa</option>
        <option value="the_scream">the_scream</option>
      </select>

      <label>Child Name</label>
      <input v-model="form.child_name" placeholder="Emma"/>

      <label>Child Age</label>
      <input v-model.number="form.child_age" type="number" min="1" max="12"/>

      <label>Family Value</label>
      <input v-model="form.family_value" placeholder="sharing"/>

      <label><input type="checkbox" v-model="form.fallback"/> Use fallback</label>

      <button :disabled="loading" style="margin-top:12px;">Generate</button>
    </form>

    <div v-if="loading" style="margin-top:16px;">Generating…</div>
    <div v-if="downloadUrl" style="margin-top:16px;">
      <a :href="apiBase + downloadUrl" target="_blank">Download PDF</a>
    </div>

    <pre v-if="error" style="color:#b00;margin-top:16px;">{{ error }}</pre>
  </div>
</template>

<script setup>
import axios from 'axios'
import { reactive, ref } from 'vue'

const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const form = reactive({
  painting_id: 'starry_night',
  child_name: 'Emma',
  child_age: 6,
  family_value: 'sharing',
  fallback: false
})
const loading = ref(false)
const downloadUrl = ref('')
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  downloadUrl.value = ''
  try {
    const { data } = await axios.post(`${apiBase}/generate`, form)
    downloadUrl.value = data.download_url
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message
  } finally {
    loading.value = false
  }
}
</script>

<style>
label { display:block; margin-top:12px; }
input, select { width:100%; padding:8px; }
button { padding:8px 12px; }
</style>
