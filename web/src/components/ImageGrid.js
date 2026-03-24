/**
 * ImageGrid — Display search results, select/deselect, drag reorder
 * Listens: images:loaded, state:images
 * Emits: state changes via state module
 */
import bus from '../core/EventBus.js'
import { getState, setImages, addImage, removeImage, reorderImages } from '../core/state.js'

let gridEl, selInfoEl

export function mount(el) {
  el.innerHTML = `
    <div class="image-grid" id="imgGrid"></div>
    <div class="sel-info" style="display:none" id="selInfo">
      <span class="count" id="selCount">0 ảnh</span>
      <div>
        <button class="btn btn-outline" id="btnSelAll">Chọn tất cả</button>
        <button class="btn btn-outline" id="btnClear">Bỏ chọn</button>
      </div>
    </div>
  `
  gridEl = el.querySelector('#imgGrid')
  selInfoEl = el.querySelector('#selInfo')

  el.querySelector('#btnSelAll').addEventListener('click', selectAll)
  el.querySelector('#btnClear').addEventListener('click', clearAll)

  bus.on('images:loaded', renderImages)
  bus.on('state:images', updateSelection)
}

function renderImages(images) {
  gridEl.innerHTML = ''
  selInfoEl.style.display = images.length ? 'flex' : 'none'

  // Keep existing selected, add new options
  images.forEach(img => {
    const div = document.createElement('div')
    div.className = 'image-item'
    div.dataset.url = img.url
    div.innerHTML = `
      <img src="${img.thumb}" alt="" loading="lazy" class="loading"
           onload="this.classList.remove('loading')"
           onerror="this.parentElement.style.display='none'" />
      <div class="check">✓</div>
      <div class="order-num"></div>
    `
    // Select/deselect
    div.addEventListener('click', () => {
      const selected = getState().selectedImages
      const exists = selected.find(s => s.url === img.url)
      if (exists) removeImage(img.url)
      else addImage(img)
    })

    // Drag reorder
    div.draggable = true
    div.addEventListener('dragstart', e => {
      e.dataTransfer.setData('text/plain', img.url)
      div.classList.add('dragging')
    })
    div.addEventListener('dragend', () => div.classList.remove('dragging'))
    div.addEventListener('dragover', e => { e.preventDefault(); div.classList.add('drop-target') })
    div.addEventListener('dragleave', () => div.classList.remove('drop-target'))
    div.addEventListener('drop', e => {
      e.preventDefault()
      div.classList.remove('drop-target')
      const fromUrl = e.dataTransfer.getData('text/plain')
      const arr = getState().selectedImages
      const fromIdx = arr.findIndex(s => s.url === fromUrl)
      const toIdx = arr.findIndex(s => s.url === img.url)
      if (fromIdx > -1 && toIdx > -1 && fromIdx !== toIdx) {
        reorderImages(fromIdx, toIdx)
      }
    })

    gridEl.appendChild(div)
  })
}

function updateSelection(selected) {
  const count = selected.length
  document.getElementById('selCount').textContent = `${count} ảnh đã chọn`

  gridEl.querySelectorAll('.image-item').forEach(item => {
    const url = item.dataset.url
    const idx = selected.findIndex(s => s.url === url)
    const num = item.querySelector('.order-num')
    if (idx > -1) {
      item.classList.add('selected')
      num.textContent = idx + 1
      num.style.display = 'flex'
    } else {
      item.classList.remove('selected')
      num.style.display = 'none'
    }
  })
}

function selectAll() {
  const all = []
  gridEl.querySelectorAll('.image-item').forEach(item => {
    if (item.style.display !== 'none') {
      all.push({ url: item.dataset.url, thumb: item.querySelector('img')?.src || '' })
    }
  })
  setImages(all)
}

function clearAll() { setImages([]) }
