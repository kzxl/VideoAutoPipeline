/**
 * SearchPanel — Source tabs + search input + upload button
 * Emits: images:loaded, toast:show
 */
import bus from '../core/EventBus.js'
import api from '../core/api.js'
import { setSource, getState } from '../core/state.js'

export function mount(el) {
  el.innerHTML = `
    <div class="source-tabs">
      <div class="source-tab active" data-src="bing">🔍 Bing</div>
      <div class="source-tab" data-src="pexels">📷 Pexels (Free)</div>
      <div class="source-tab" data-src="upload">📤 Upload</div>
    </div>
    <div class="flex-row">
      <div class="fg" style="flex:3">
        <input type="text" id="topic" placeholder="VD: Canon 5D Mark II, landscape, technology..." />
      </div>
      <button class="btn btn-primary" id="btnSearch">🔍 Tìm ảnh</button>
    </div>
    <div id="uploadArea" class="upload-area" style="display:none">
      📤 Kéo thả hoặc click để upload ảnh từ máy
      <input type="file" id="uploadInput" accept="image/*" multiple style="display:none" />
    </div>
  `

  // Source tabs
  el.querySelectorAll('.source-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      el.querySelectorAll('.source-tab').forEach(t => t.classList.remove('active'))
      tab.classList.add('active')
      const src = tab.dataset.src
      setSource(src)
      el.querySelector('#uploadArea').style.display = src === 'upload' ? 'block' : 'none'
      el.querySelector('#btnSearch').style.display = src === 'upload' ? 'none' : 'inline-flex'
      el.querySelector('#topic').parentElement.style.display = src === 'upload' ? 'none' : 'block'
    })
  })

  // Search
  const doSearch = async () => {
    const topic = el.querySelector('#topic').value.trim()
    if (!topic) return bus.emit('toast:show', { msg: 'Nhập chủ đề!', type: 'error' })
    const btn = el.querySelector('#btnSearch')
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Tìm...'
    try {
      const d = await api.search(topic, getState().currentSource)
      if (d.error) return bus.emit('toast:show', { msg: d.error, type: 'error' })
      bus.emit('images:loaded', d.images)
    } catch (e) { bus.emit('toast:show', { msg: 'Search failed', type: 'error' }) }
    finally { btn.disabled = false; btn.innerHTML = '🔍 Tìm ảnh' }
  }
  el.querySelector('#btnSearch').addEventListener('click', doSearch)
  el.querySelector('#topic').addEventListener('keydown', e => { if (e.key === 'Enter') doSearch() })

  // Upload
  const uploadArea = el.querySelector('#uploadArea')
  const uploadInput = el.querySelector('#uploadInput')
  uploadArea.addEventListener('click', () => uploadInput.click())
  uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.style.borderColor = 'var(--accent)' })
  uploadArea.addEventListener('dragleave', () => { uploadArea.style.borderColor = '' })
  uploadArea.addEventListener('drop', async (e) => {
    e.preventDefault(); uploadArea.style.borderColor = ''
    const files = [...e.dataTransfer.files].filter(f => f.type.startsWith('image/'))
    if (files.length) await handleUpload(files)
  })
  uploadInput.addEventListener('change', async () => {
    if (uploadInput.files.length) await handleUpload([...uploadInput.files])
  })

  async function handleUpload(files) {
    try {
      const d = await api.uploadImages(files)
      if (d.images) bus.emit('images:loaded', d.images)
      bus.emit('toast:show', { msg: `${d.count} ảnh uploaded!`, type: 'ok' })
    } catch (e) { bus.emit('toast:show', { msg: 'Upload failed', type: 'error' }) }
  }
}
