import { helpers } from './module.mjs';

// Search
let input = document.querySelector('.input_query');
let activeRequest = null;
let data = input.addEventListener('input', () => helpers.search(input, activeRequest));

// Show detail information of item
/*
let item = document.querySelector(".result-item span");
console.log(item);
console.log(data);
if (item != null && data != null) {
    item.addEventListener('click', (event) => helpers.triggerModal(data));
}
*/