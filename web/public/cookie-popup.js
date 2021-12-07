export function renderCookiePopUp() {
    const hasCookie = cookieCheck()
    const cookiePopUp = document.querySelector('cookie-popup');
    cookiePopUp.innerHTML = `
      <div class="footer" >
      </div>
    `;

}

function cookieCheck() {
    return true;
}