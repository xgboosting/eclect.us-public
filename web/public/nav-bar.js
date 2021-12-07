export function renderNavBar(route) {
    const navBar = document.querySelector('nav-bar');
    navBar.innerHTML = `
    <nav class="navbar navbar-expand-sm">
      <a class="navbar-brand ml-4" href="#">eclect.us 🦜</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav">
          <li class="nav-item ${route === 'about' ? 'navbar-link-active': 'navbar-link'}">
            <a class="nav-link" href="#">About 📜</a>
          </li>
          <li class="nav-item ${route === 'recents' ? 'navbar-link-active': 'navbar-link'}">
            <a class="nav-link" href="#recents">Recents 📆</a>
          </li>
        </ul>
        <a class="nav-link" target="_blank" href="https://discord.gg/XpkZEBR"><img src="/static/img/discord.svg" height="50" width="50" alt="discord"></a>
      </div>
    </nav>
    `;

}
