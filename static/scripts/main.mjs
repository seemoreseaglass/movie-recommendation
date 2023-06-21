import { helpers } from './module.mjs';

// Search
function searchCode() {
    let input = document.querySelector('.input_query');
    let activeRequest = null;
    input.addEventListener('input', () => helpers.search(input, activeRequest));
}

if (window.location.pathname === '/') {
    console.log("index.html");
    searchCode();
} else if (window.location.pathname === '/favorite') {
    console.log("favorite.html");
    helpers.likebtnListenerBinder();
} else if (window.location.pathname === '/recommend_collab') {
    console.log("recommend_collab.html");
    helpers.likebtnListenerBinder();
} else {
    console.log("other page");
}
