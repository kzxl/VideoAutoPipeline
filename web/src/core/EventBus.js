/**
 * EventBus — Indirect Communication (UArch Principle #5)
 * Components communicate via events, never import each other.
 */
const listeners = new Map()

export function on(event, handler) {
  if (!listeners.has(event)) listeners.set(event, [])
  listeners.get(event).push(handler)
}

export function off(event, handler) {
  if (!listeners.has(event)) return
  const arr = listeners.get(event)
  const idx = arr.indexOf(handler)
  if (idx > -1) arr.splice(idx, 1)
}

export function emit(event, data) {
  if (!listeners.has(event)) return
  listeners.get(event).forEach(fn => fn(data))
}

export default { on, off, emit }
