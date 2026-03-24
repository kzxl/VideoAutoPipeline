/**
 * State — Data Sovereignty (UArch Principle #6)
 * Shared reactive state. Components read/write via state,
 * and emit events when state changes.
 */
import bus from './EventBus.js'

const _state = {
  selectedImages: [],   // [{url, thumb, title, uploaded?}]
  currentFormat: '9:16',
  currentSource: 'bing',
}

export function getState() { return _state }

export function setImages(images) {
  _state.selectedImages = images
  bus.emit('state:images', images)
}

export function addImage(img) {
  _state.selectedImages.push(img)
  bus.emit('state:images', _state.selectedImages)
}

export function removeImage(url) {
  _state.selectedImages = _state.selectedImages.filter(i => i.url !== url)
  bus.emit('state:images', _state.selectedImages)
}

export function reorderImages(from, to) {
  const arr = _state.selectedImages
  const [item] = arr.splice(from, 1)
  arr.splice(to, 0, item)
  bus.emit('state:images', arr)
}

export function setFormat(fmt) {
  _state.currentFormat = fmt
  bus.emit('state:format', fmt)
}

export function setSource(src) {
  _state.currentSource = src
  bus.emit('state:source', src)
}

export default { getState, setImages, addImage, removeImage, reorderImages, setFormat, setSource }
