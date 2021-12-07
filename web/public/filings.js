import { makeCard } from './filing-static.js';
import { makeLoadingCard } from './filing-loading.js';
import { renderEmptyCards } from './empty-filings.js'

export function renderFilings(symbol) {
    const content = document.querySelector('content');
    const pages = document.querySelector('pages');
    pages.innerHTML = '';
    content.innerHTML = `
            <div class="container pt-5">
            <div class="row">
                ${makeLoadingCard()}
            </div>
            </div>
            `;
    const url = `https://api.eclect.us/symbol/${symbol}`
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                renderEmptyCards(content)
            } else {
                const cards = data.map(makeCard)
                content.innerHTML = `
                <div class="container pt-5">
                <div class="row">
                    ${cards.join('\n')}
                </div>
                </div>
                `;
        }
    });
}
