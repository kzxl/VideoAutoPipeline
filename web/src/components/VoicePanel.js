/**
 * VoicePanel — TTS voice selector + speed slider + preview
 * Emits: audio:ready, toast:show
 */
import bus from '../core/EventBus.js'
import api from '../core/api.js'

const VOICES = [
  { group: '🇻🇳 Tiếng Việt', voices: [
    { id: 'vi-VN-NamMinhNeural', name: 'Nam Minh — Nam' },
    { id: 'vi-VN-HoaiMyNeural', name: 'Hoài My — Nữ' },
  ]},
  { group: '🇺🇸 English', voices: [
    { id: 'en-US-GuyNeural', name: 'Guy — Male' },
    { id: 'en-US-JennyNeural', name: 'Jenny — Female' },
    { id: 'en-US-AriaNeural', name: 'Aria — Conversational' },
    { id: 'en-GB-RyanNeural', name: 'Ryan — UK' },
  ]},
  { group: '🇯🇵 日本語', voices: [
    { id: 'ja-JP-KeitaNeural', name: 'Keita — Male' },
    { id: 'ja-JP-NanamiNeural', name: 'Nanami — Female' },
  ]},
  { group: '🇰🇷 한국어', voices: [
    { id: 'ko-KR-InJoonNeural', name: 'InJoon — Male' },
    { id: 'ko-KR-SunHiNeural', name: 'SunHi — Female' },
  ]},
  { group: '🇨🇳 中文', voices: [
    { id: 'zh-CN-YunxiNeural', name: 'Yunxi — Male' },
    { id: 'zh-CN-XiaoxiaoNeural', name: 'Xiaoxiao — Female' },
  ]},
]

export function mount(el) {
  const optGroups = VOICES.map(g =>
    `<optgroup label="${g.group}">${g.voices.map(v =>
      `<option value="${v.id}">${v.name}</option>`
    ).join('')}</optgroup>`
  ).join('')

  el.innerHTML = `
    <div class="fg">
      <label>Giọng TTS</label>
      <select id="voice">${optGroups}</select>
    </div>
    <div class="fg mt-sm">
      <label>Tốc độ: <strong id="rateLabel">Bình thường</strong></label>
      <input type="range" id="rateSlider" min="-50" max="50" value="0" step="5" />
    </div>
    <div class="mt-md">
      <button class="btn btn-outline" id="btnPreview">▶ Nghe thử</button>
    </div>
  `

  // Rate label
  const slider = el.querySelector('#rateSlider')
  const label = el.querySelector('#rateLabel')
  slider.addEventListener('input', () => {
    const v = parseInt(slider.value)
    label.textContent = v === 0 ? 'Bình thường' : v > 0 ? `Nhanh +${v}%` : `Chậm ${v}%`
  })

  // Preview
  el.querySelector('#btnPreview').addEventListener('click', async () => {
    const text = document.getElementById('narration')?.value.trim()
    if (!text) return bus.emit('toast:show', { msg: 'Nhập nội dung!', type: 'error' })
    const btn = el.querySelector('#btnPreview')
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Tạo...'
    try {
      const rate = getRate(slider)
      const d = await api.previewAudio(text, el.querySelector('#voice').value, rate)
      if (d.error) return bus.emit('toast:show', { msg: d.error, type: 'error' })
      bus.emit('audio:ready', d.audio_url)
    } catch (e) { bus.emit('toast:show', { msg: 'Preview failed', type: 'error' }) }
    finally { btn.disabled = false; btn.innerHTML = '▶ Nghe thử' }
  })
}

function getRate(slider) {
  const v = parseInt(slider.value)
  return v === 0 ? '0' : v > 0 ? `+${v}%` : `${v}%`
}

export function getVoiceConfig() {
  return {
    voice: document.getElementById('voice')?.value || 'vi-VN-NamMinhNeural',
    rate: getRate(document.getElementById('rateSlider')),
  }
}
