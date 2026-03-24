/**
 * Toast — Notification popup
 * Listens: toast:show
 */
import bus from '../core/EventBus.js'

let timer

export function mount() {
  const el = document.getElementById('toast')
  bus.on('toast:show', ({ msg, type = 'error' }) => {
    clearTimeout(timer)
    el.textContent = msg
    el.className = 'toast ' + type
    el.style.display = 'block'
    timer = setTimeout(() => { el.style.display = 'none' }, 3000)
  })
}
