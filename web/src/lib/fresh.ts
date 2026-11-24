const RELOADED = 'climb.reloaded-for'

/** A page's chunk gone after a deploy: reload once onto the new build. `web-app/README.md` */
export function reloadOnStaleChunk() {
  window.addEventListener('vite:preloadError', (event) => {
    // once per build: a chunk missing from the new build too would reload forever
    if (sessionStorage.getItem(RELOADED) === __BUILT__) return
    sessionStorage.setItem(RELOADED, __BUILT__)
    event.preventDefault()
    window.location.reload()
  })
}
