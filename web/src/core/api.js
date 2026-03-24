/**
 * API Client — Contract-First (UArch Principle #3)
 * All backend communication goes through this single interface.
 */
const BASE = ''  // Vite proxy handles /api → Flask

async function post(url, body) {
  const r = await fetch(BASE + url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return r.json()
}

async function postForm(url, formData) {
  const r = await fetch(BASE + url, { method: 'POST', body: formData })
  return r.json()
}

async function get(url) {
  const r = await fetch(BASE + url)
  return r.json()
}

// ── Contracts ──
export const api = {
  search:       (topic, source) => post('/api/search', { topic, source }),
  previewAudio: (text, voice, rate) => post('/api/preview-audio', { text, voice, rate }),
  generate:     (payload) => post('/api/generate', payload),
  progress:     () => get('/api/progress'),
  uploadMusic:  (file) => { const fd = new FormData(); fd.append('file', file); return postForm('/api/upload-music', fd) },
  removeMusic:  () => post('/api/remove-music', {}),
  uploadImages: (files) => { const fd = new FormData(); files.forEach(f => fd.append('files', f)); return postForm('/api/upload-images', fd) },
  generateScript: (topic, lang) => post('/api/generate-script', { topic, lang }),
}

export default api
