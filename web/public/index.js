import { renderNavBar } from './nav-bar.js';
import { renderSearch } from './search.js';
import { renderFilings } from './filings.js';
import { renderRecents } from './recents.js';
import { renderAbout } from './about.js';
import { renderCookiePopUp } from './cookie-popup.js'

window.addEventListener('load', () => {
    registerSW()
    const navBar = document.createElement('nav-bar');
    const search = document.createElement('search');
    const content = document.createElement('content');
    const pages = document.createElement('pages')
    const cookiePopUp = document.createElement('cookie-popup')
    const main = document.querySelector('main');
    main.appendChild(navBar);
    main.appendChild(search);
    main.appendChild(content);
    main.appendChild(pages);
    main.append(cookiePopUp)
    render(document.location.hash)
    renderSearch()
    //renderCookiePopUp()
    window.addEventListener('popstate', function(){
        render(document.location.hash);
    })
});


function render(hashUrl) {
    let url = hashUrl.replace('#', '');
    const urlList = url.split('/')
    switch (urlList[0]) {
        case 'recents':
            renderNavBar('recents')
            renderRecents(urlList[1])
            break;
        case 'search':
            document.querySelector('pages').innerHTML = ''
            renderNavBar('search')
            renderFilings(urlList[1])
            break;
        default:
            document.querySelector('pages').innerHTML = ''
            renderNavBar('about')
            renderAbout()
            break;
    }
} 


async function registerSW() {
  if ('serviceWorker' in navigator) {
    try {
      await navigator.serviceWorker.register('./sw.js');
    } catch (e) {
      console.log(`SW registration failed`);
    }
  }
}
