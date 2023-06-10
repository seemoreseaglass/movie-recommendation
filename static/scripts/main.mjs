import helpers from './module.mjs';

// Search
let input = document.querySelector('.input_query');
let activeRequest = null;
input.addEventListener('input', helpers.search(input, activeRequest));