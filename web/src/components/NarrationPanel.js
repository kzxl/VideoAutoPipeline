/**
 * NarrationPanel — Narration textarea + AI script generation
 * Emits: toast:show
 */
import bus from '../core/EventBus.js'
import api from '../core/api.js'

export function mount(el) {
  el.innerHTML = `
    <div class="flex-row" style="gap:6px;margin-bottom:6px;align-items:center">
      <input type="text" id="scriptTopic" placeholder="Nhập chủ đề để AI viết script..." style="flex:2" />
      <button class="btn btn-warn" id="btnGenScript">✨ AI Script</button>
    </div>
    <textarea id="narration" rows="4" placeholder="Viết nội dung giọng đọc cho video hoặc dùng AI Script ở trên..."></textarea>
    <div class="audio-section" id="audioSection">
      <audio id="previewAudio" controls></audio>
    </div>
  `

  // AI Script generation
  el.querySelector('#btnGenScript').addEventListener('click', async () => {
    const topic = el.querySelector('#scriptTopic').value.trim()
    if (!topic) return bus.emit('toast:show', { msg: 'Nhập chủ đề script!', type: 'error' })
    const btn = el.querySelector('#btnGenScript')
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Đang viết...'
    try {
      const d = await api.generateScript(topic, 'vi')
      if (d.error) return bus.emit('toast:show', { msg: d.error, type: 'error' })
      el.querySelector('#narration').value = d.script
      bus.emit('toast:show', { msg: 'Script generated!', type: 'ok' })
    } catch (e) {
      bus.emit('toast:show', { msg: 'AI Script failed: ' + e.message, type: 'error' })
    } finally { btn.disabled = false; btn.innerHTML = '✨ AI Script' }
  })

  // Listen for audio preview response
  bus.on('audio:ready', (url) => {
    const section = el.querySelector('#audioSection')
    const audio = el.querySelector('#previewAudio')
    section.style.display = 'block'
    audio.src = url
    audio.play()
  })
}
