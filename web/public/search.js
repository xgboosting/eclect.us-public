import { symbols } from './static/symbols.js';

function search() {
    const search = document.querySelector('search');
    search.innerHTML = `
    <div class="container pt-5">
      <div class="row">
        <div class="card pt-3 pb-3">
          <p>Search by ticker or company name</p>
            <input class="autocomplete" id="autocomplete" type="search" placeholder="Search" aria-label="Search">
        </div>
      </div>
    </div>
    `;
}

export function renderSearch() {
  search()
  //let symbols = [];
  //fetch('http://localhost:8000/supported-symbols')
  //.then(response => response.json())
  //.then(data => symbols = data);
  const input = document.getElementById("autocomplete");

  autocomplete({
        input: input,
        fetch: function(text, update) {
            text = text.toLowerCase();
            let suggestions = symbols.filter(n => n.label.toLowerCase().includes(text))
            update(suggestions.slice(0, 10));
        },
        onSelect: function(item) {
            location.hash = `#search/${item.value}`;
            document
			      .querySelector("#autocomplete")
			      .setAttribute("placeholder", item.value);
            input.value = "";
        }
    }); 
}
