/**
 * GeneratePanel — Generate button, progress steps, video player
 * Uses api.js for generate + progress polling
 */
import bus from '../core/EventBus.js'
import api from '../core/api.js'
import { getState } from '../core/state.js'
import { getVoiceConfig } from './VoicePanel.js'
import { getOptions } from './OptionsPanel.js'

export function mount(el) {
  el.innerHTML = `
    <button class="btn btn-success" id="btnGenerate" style="font-size:14px;padding:9px 20px">🎬 Generate Video</button>
    <div id="progressArea" style="display:none">
      <div class="progress-bar"><div class="fill" id="progressFill"></div></div>
      <div class="progress-steps" id="progressSteps"></div>
    </div>
    <div class="video-result" id="videoResult">
      <video id="videoPlayer" controls></video>
      <div class="video-meta">
        <span>Duration: <strong id="metaDur">-</strong></span>
        <span>Size: <strong id="metaSize">-</strong></span>
        <span>Res: <strong id="metaRes">-</strong></span>
      </div>
      <div class="mt-md"><a id="downloadLink" class="btn btn-primary" download="video.mp4">⬇ Download</a></div>
    </div>
  `

  el.querySelector('#btnGenerate').addEventListener('click', generate)
}

async function generate() {
  const narration = document.getElementById('narration')?.value.trim()
  const state = getState()
  if (!narration) return bus.emit('toast:show', { msg: 'Nhập nội dung TTS!', type: 'error' })
  if (state.selectedImages.length < 2) return bus.emit('toast:show', { msg: 'Chọn ít nhất 2 ảnh!', type: 'error' })

  const btn = document.getElementById('btnGenerate')
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Đang tạo...'
  document.getElementById('progressArea').style.display = 'block'
  document.getElementById('videoResult').style.display = 'none'

  // Progress polling
  const pi = setInterval(async () => {
    try {
      const p = await api.progress()
      document.getElementById('progressFill').style.width = p.percent + '%'
      if (p.steps?.length) {
        const icons = { pending: '○', running: '◉', done: '✓', error: '✕' }
        document.getElementById('progressSteps').innerHTML = p.steps.map(s =>
          `<div class="pstep ${s.status}"><span class="icon">${icons[s.status] || '○'}</span><span>${s.name}</span><span class="detail">${s.detail || ''}</span></div>`
        ).join('')
      }
    } catch (e) {}
  }, 600)

  try {
    const voiceCfg = getVoiceConfig()
    const opts = getOptions()
    const d = await api.generate({
      narration,
      images: state.selectedImages.map(i => i.url),
      voice: voiceCfg.voice,
      rate: voiceCfg.rate,
      ...opts,
    })
    clearInterval(pi)
    if (d.error) {
      bus.emit('toast:show', { msg: d.error, type: 'error' })
      document.getElementById('progressArea').style.display = 'none'
      return
    }
    document.getElementById('progressFill').style.width = '100%'
    document.getElementById('videoResult').style.display = 'block'
    document.getElementById('videoPlayer').src = d.video_url
    document.getElementById('metaDur').textContent = d.duration + 's'
    document.getElementById('metaSize').textContent = d.size_mb + ' MB'
    document.getElementById('metaRes').textContent = d.resolution
    document.getElementById('downloadLink').href = d.video_url
    bus.emit('toast:show', { msg: 'Video tạo thành công!', type: 'ok' })
  } catch (e) {
    clearInterval(pi)
    bus.emit('toast:show', { msg: 'Error: ' + e.message, type: 'error' })
  } finally { btn.disabled = false; btn.innerHTML = '🎬 Generate Video' }
}
