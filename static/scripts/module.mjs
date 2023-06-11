function createTableContents(data, input) {
    let html_titles = '';
    let html_names = '';
    if (Object.keys(data).length != 0) {

        // Generate html for titles query
        if (data.titles.length != 0) {
            let titles = data.titles;
            for (let i in titles) {
                let titleId = titles[i].titleId;
                let title = titles[i].primaryTitle.replace('<', '&lt;').replace('&', '&amp;');
                let action = titles[i].liked ? 'unlike' : 'like';
                html_titles += '<tr><td>' + title + '</td><td><button class="like" onclick="likeUnlike(event, \'' + titleId + '\', \'' + action + '\')">' + action + '</button></td></tr>';
            }

        }
        // Generate html for principals query
        if (data.names.length != 0) {
            let names = data.names;
            for (let i in names) {
                let personId = names[i].personId;
                let primaryName = names[i].primaryName.replace('<', '&lt;').replace('&', '&amp;');
                let action = names[i].liked ? 'unlike' : 'like';
                html_names += '<tr><td>' + primaryName + '</td><td><button class="like" onclick="likeUnlike(event, \'' + personId + '\', \'' + action + '\')">' + action + '</button></td></tr>';
            }
        }
    } else {
        html_titles = 'Not Found';
        html_names = 'Not Found';
    }

            // Update page
            document.querySelector('.q-result-titles').innerHTML = html_titles;
            document.querySelector('.q-result-names').innerHTML = html_names;
        }

async function search(input, activeRequest) {
    // Check if there's an active request, and if so, abort it
    if (activeRequest) {
        activeRequest.abort();
    }

    // Create a new request and store it as the active request
    let request = new Request('/search?q=' + input.value);
    activeRequest = request;

    try {
        let response = await fetch(request);
        let data = await response.json();

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
        event.target.setAttribute('onclick', `likeUnlike(event, '${itemId}', 'unlike')`);
    } else if (result.status === 'Unliked') {
        event.target.textContent = 'like';
        event.target.setAttribute('onclick', `likeUnlike(event, '${itemId}', 'like')`);
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

// Export functions as 

export const helpers = {
    search: search,
    likeUnlike: likeUnlike
};