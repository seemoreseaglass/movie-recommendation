import { helpers } from './module.mjs';

// Search
let input = document.querySelector('.input_query');
console.log("input: ", input);
let activeRequest = null;
console.log("point 2");
let data = input.addEventListener('input', () => helpers.search(input, activeRequest));
console.log("data: ", data);
let aon = input.addEventListener('input', function() {
    console.log("アオン　アオン　アオン");
});

// Show detail information of item
let item = document.querySelector(".result-item")
console.log("point 4");
if (item != null && data != null) {
    console.log("point 5");
    item.addEventListener('click', () => helpers.triggerModal(data));
    console.log("point 6");
}
