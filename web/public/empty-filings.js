export function renderEmptyCards(content) {
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