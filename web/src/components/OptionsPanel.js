/**
 * OptionsPanel — Format selector, effects toggles, music upload
 */
import bus from '../core/EventBus.js'
import api from '../core/api.js'
import { setFormat } from '../core/state.js'

export function mount(el) {
  el.innerHTML = `
    <div class="three-col">
      <div>
        <label>Định dạng</label>
        <div class="format-options">
          <div class="format-btn active" data-format="9:16">📱 9:16<br><small>TikTok</small></div>
          <div class="format-btn" data-format="16:9">🖥 16:9<br><small>YouTube</small></div>
          <div class="format-btn" data-format="1:1">📷 1:1<br><small>Instagram</small></div>
        </div>
      </div>
      <div>
        <label>Hiệu ứng</label>
        <div>
          <label class="pill active"><input type="checkbox" id="optKenBurns" checked> Ken Burns (zoom)</label>
          <label class="pill active"><input type="checkbox" id="optCrossfade" checked> Crossfade</label>
          <label class="pill"><input type="checkbox" id="optSubtitle"> Phụ đề</label>
        </div>
      </div>
      <div>
        <label>Nhạc nền</label>
        <div class="music-area" id="musicArea">
          🎵 Upload nhạc (.mp3)
          <input type="file" id="musicFile" accept=".mp3,.wav,.ogg" style="display:none" />
        </div>
        <div class="music-info" id="musicInfo" style="display:none">
          <span id="musicName">-</span>
          <div style="display:flex;align-items:center;gap:4px">
            <span style="font-size:10px;color:var(--text2)">Vol:<span id="volLabel">15%</span></span>
            <input type="range" id="musicVol" min="5" max="50" value="15" step="5" style="width:60px" />
            <button class="btn btn-outline" style="padding:2px 6px" id="btnRemoveMusic">✕</button>
          </div>
        </div>
      </div>
    </div>
  `

  // Format buttons
  el.querySelectorAll('.format-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      el.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'))
      btn.classList.add('active')
      setFormat(btn.dataset.format)
    })
  })

  // Effect pills toggle
  el.querySelectorAll('.pill input[type=checkbox]').forEach(cb => {
    cb.addEventListener('change', () => cb.parentElement.classList.toggle('active'))
  })

  // Music upload
  const musicArea = el.querySelector('#musicArea')
  const musicFile = el.querySelector('#musicFile')
  musicArea.addEventListener('click', () => musicFile.click())
  musicFile.addEventListener('change', async () => {
    if (!musicFile.files.length) return
    try {
      const d = await api.uploadMusic(musicFile.files[0])
      if (d.error) return bus.emit('toast:show', { msg: d.error, type: 'error' })
      musicArea.style.display = 'none'
      el.querySelector('#musicInfo').style.display = 'flex'
      el.querySelector('#musicName').textContent = `🎵 ${d.filename} (${d.duration}s)`
      bus.emit('toast:show', { msg: 'Nhạc uploaded!', type: 'ok' })
    } catch (e) { bus.emit('toast:show', { msg: 'Upload failed', type: 'error' }) }
  })

  // Volume label
  el.querySelector('#musicVol').addEventListener('input', (e) => {
    el.querySelector('#volLabel').textContent = e.target.value + '%'
  })

  // Remove music
  el.querySelector('#btnRemoveMusic').addEventListener('click', async () => {
    await api.removeMusic()
    musicArea.style.display = 'block'
    el.querySelector('#musicInfo').style.display = 'none'
    musicFile.value = ''
  })
}

export function getOptions() {
  return {
    format: document.querySelector('.format-btn.active')?.dataset.format || '9:16',
    kenburns: document.getElementById('optKenBurns')?.checked ?? true,
    crossfade: document.getElementById('optCrossfade')?.checked ?? true,
    subtitle: document.getElementById('optSubtitle')?.checked ?? false,
    musicVolume: parseInt(document.getElementById('musicVol')?.value || '15') / 100,
  }
}
