function createTableContents(data) {
    let html_titles = '';
    let html_names = '';
    if (Object.keys(data).length != 0) {

        // Generate html for titles query
        if (data.titles.length != 0) {
            let titles = data.titles;
            for (const [key, value] of Object.entries(titles)) {
                let titleId = key;
                let title = value['primaryTitle'].replace('<', '&lt;').replace('&', '&amp;');
                let action = value['liked'] ? 'unlike' : 'like';
                html_titles += '<tr><td class="result-item" id="\'' + titleId + '\'"><span>' + title + '</span></td><td><button class="like" data-id="' + titleId + '">' + action + '</button></td></tr>';
            }

        }
        // Generate html for principals query
        if (data.names.length != 0) {
            let names = data.names;
            for (const [key, value] of Object.entries(names)) {
                let personId = key;
                let primaryName = value['primaryName'].replace('<', '&lt;').replace('&', '&amp;');
                let action = value['liked'] ? 'unlike' : 'like';
                html_names += '<tr><td class="result-item" id="\'' + personId + '\'"><span>' + primaryName + '</span></td><td><button class="like" data-id="' + personId + '">' + action + '</button></td></tr>';
            }
        }
    } else {
        html_titles = 'Not Found';
        html_names = 'Not Found';
    }

    // Update page
    document.querySelector('.q-result-titles').innerHTML = html_titles;
    document.querySelector('.q-result-names').innerHTML = html_names;


    // Bind the event listener to the parent element using event delegation
    let table = document.querySelector('.q-result-titles');
    table.addEventListener('click', (event) => {
        if (event.target.classList.contains('like')) {
            let itemId = event.target.dataset.id;
            helpers.likeUnlike(event, itemId, 'like');
        } else if (event.target.classList.contains('unlike')) {
            let itemId = event.target.dataset.id;
            helpers.likeUnlike(event, itemId, 'unlike');
        }
    });
        }

async function search(input, activeRequest) {
    // Check if there's an active request, and if so, abort it
    if (activeRequest) {
        activeRequest.abort();
    } else {
        console.log("no active request");
    }

    // Create a new request and store it as the active request
    let request = new Request('/search?q=' + input.value);
    activeRequest = request;

    // Define return variable
    let data = null;

    try {
        let response = await fetch(request);
        data = await response.json();

        // Check if the current request is still the active request
        if (request === activeRequest) {
            createTableContents(data, input);
            activeRequest = null;
        }
    } catch (error) {
        // Handle any errors
        console.error(error);

        // Reset the active request to null
        activeRequest = null;
    }
    let item = document.querySelector(".result-item")
    console.log("item: " + item);
    console.log("data: " + data);
    if (item != null && data != null) {
        item.addEventListener('click', () => triggerModal(data));
    }
    return data
}


async function likeUnlike(event, itemId, action) {
    event.preventDefault();

    // Send request
    let requestData = {
        itemId: itemId,
        action: action
    };

    // Get response
    let response = await fetch('/like', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    });
    
    // Update button
    let result = await response.json();
    if (result.status === 'Liked') {
        event.target.textContent = 'unlike';
        event.target.classList.remove('like');
        event.target.classList.add('unlike');

    } else if (result.status === 'Unliked') {
        event.target.textContent = 'like';
        event.target.classList.remove('unlike');
        event.target.classList.add('like');
    } else if (typeof result.error !== 'undefined') {
        let alertDiv = document.querySelector('.alert-div');
        
        // Create the alert element
        let alertElement = document.createElement('div');
        alertElement.className = 'alert alert-warning mb-0 text-center';
        alertElement.textContent = result.error;
        
        // Append the alert element to the alert-div
        alertDiv.appendChild(alertElement);
        
        // Fade out after 2 seconds
        setTimeout(function() {
            alertElement.classList.add('fade');
            alertElement.style.transition = 'opacity 0.5s';
            alertElement.style.opacity = 0;
            
            setTimeout(function() {
                alertDiv.removeChild(alertElement);
            }, 500); // Remove the alert element from the DOM after fade out
        }, 2000); // Fade out after 2 seconds
    } else {
        let alertDiv = document.querySelector('.alert-div');
        
        // Create the alert element
        let alertElement = document.createElement('div');
        alertElement.className = 'alert alert-warning mb-0 text-center';
        alertElement.textContent = "Something went wrong. Please try again later.";

        // Append the alert element to the alert-div
        alertDiv.appendChild(alertElement);
        
        // Fade out after 2 seconds
        setTimeout(function() {
            alertElement.classList.add('fade');
            alertElement.style.transition = 'opacity 0.5s';
            alertElement.style.opacity = 0;
            
            setTimeout(function() {
                alertDiv.removeChild(alertElement);
            }, 500); // Remove the alert element from the DOM after fade out
        }, 2000); // Fade out after 2 seconds
    }
}


function triggerModal(event, data) {
    if (event === undefined) {
        console.log("event is undefined");
    }
    console.log("target is: " + event.target);
    event.preventDefault();
    console.log("I'm gonna print the event")
    console.log("event: " + event);
    let itemId = event.target.id;
    let modal = document.getElementById("exampleModal");
    let modalTitle = document.querySelector(".modal-title");
    let modalBody = document.querySelector(".modal-body");
    let titleContent = '';
    let bodyContent = document.createElement('ul');
    if (itemId && itemId[0] === 't') {
        // If item is title
        // Set variables
        data = data['titles'][itemId];
        for (const [key, value] of Object.entries(data)) {
            if (key === 'primaryTitle') {
                titleContent.innerHTML = value;
            } else {
                let list = document.createElement('li');
                list.textContent = value;
                bodyContent.appendChild(list);
            }
        }
    } else if (itemId) {
        // If item is person
        // Set variables
        data = data['names'][itemId];
        for (const [key, value] of Object.entries(data)) {
            if (key === 'primaryName') {
                titleContent.innerHTML = value;
            } else {
                let list = document.createElement('li');
                list.textContent = value;
                bodyContent.appendChild(list);
            }
        }
    }

    modalTitle.innerHTML = titleContent;
    modalBody.innerHTML = '';
    modalBody.innerHTML = bodyContent;
    
    // Make modal appear
    if (modal) {
        modal.classList.add('show');
    }
}



// Export functions as 

export const helpers = {
    search: search,
    likeUnlike: likeUnlike,
    triggerModal: triggerModal,
};