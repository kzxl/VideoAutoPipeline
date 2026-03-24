/**
 * Main — Registry (UArch Principle #4)
 * Auto-discover and mount all components.
 */
import './style.css'

import { mount as mountSearch } from './components/SearchPanel.js'
import { mount as mountGrid } from './components/ImageGrid.js'
import { mount as mountNarration } from './components/NarrationPanel.js'
import { mount as mountVoice } from './components/VoicePanel.js'
import { mount as mountOptions } from './components/OptionsPanel.js'
import { mount as mountGenerate } from './components/GeneratePanel.js'
import { mount as mountToast } from './components/Toast.js'

// ── Registry: mount components to their containers ──
const registry = [
  ['#searchPanel', mountSearch],
  ['#imageGrid', mountGrid],
  ['#narrationPanel', mountNarration],
  ['#voicePanel', mountVoice],
  ['#optionsPanel', mountOptions],
  ['#generatePanel', mountGenerate],
]

document.addEventListener('DOMContentLoaded', () => {
  registry.forEach(([selector, mountFn]) => {
    const el = document.querySelector(selector)
    if (el) mountFn(el)
  })
  mountToast()  // Global, no container needed
})
