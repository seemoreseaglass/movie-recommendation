import { helpers } from './module.mjs';

// Search
let input = document.querySelector('.input_query');
let activeRequest = null;
let data = input.addEventListener('input', () => helpers.search(input, activeRequest));

