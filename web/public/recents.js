import { makeCard } from './filing-static.js';
import { makeLoadingCard } from './filing-loading.js';

export function renderRecents(page=1) {
    const content = document.querySelector('content');
    renderPagesNavigation(page)
    content.innerHTML = `
            <div class="container pt-5">
            <div class="row">
                ${makeLoadingCard()}
            </div>
            </div>
            `;
    const url = `https://api.eclect.us/recents?page=${page}`;
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
    renderPagesNavigation(page)
}

function renderEmptyCards(content) {
    content.innerHTML = `
    <div class="container pt-5">
    <div class="row">
    <div class="card pt-3 pb-3 mb-5">
    <div class="flex-wrap">
    <div class="filing">
    <div class="row">
    <div class="col">
        <p role="img" aria-label="pensive smiley">There doesn't seem to be anything here 😔</p>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    `;
}

function renderPagesNavigation(page) {
    page = parseInt(page)
    const pages = document.querySelector('pages')
    pages.innerHTML = `
    <div class="container mb-5">
    <div class="row">
    <div class="col-sm text-left">
    ${
        (page > 1) ? `<a class="pages-link" href="/#recents/${page - 1}">< Prev</a>` : ''
    }
    </div>
    <div class="col-sm">
    </div>
    <div class="col-sm text-right">
            <a class="pages-link" href="/#recents/${page + 1}">Next ></a>
    </div>
    </div>
    </div>
    `
    scroll(0,0)
}
