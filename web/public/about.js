export function renderAbout() {
    const content = document.querySelector('content');
    content.innerHTML = `
    <div class="container pt-5">
    <div class="row">
        <div class="card pt-3 pb-3">
        <p>Save time reading SEC filings with the help of machine learning.</p><br>
        <p>You can read how it works <a href='https://medium.com/@gonnellcough/predicting-equity-price-movement-from-financial-statements-using-nlp-c324b3f95bd'>here</a>.</p><br>
        <p>Search for a company or browse <a href='#recents'>recents</a></p>
	<p> contact me at <a href="#" class="cryptedmail"
   	data-name="gonnellcough"
   	data-domain="gmail"
   	data-tld="com"
   	onclick="window.location.href = 'mailto:' + this.dataset.name + '@' + this.dataset.domain + '.' + this.dataset.tld; return false;"></a> if you'd like to hire me for nlp, machine learning or web development work</p>
        </div>
    </div>
    </div>
    `;
}
