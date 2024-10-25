let token = null;

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username, password})
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            token = data.access_token;
            document.getElementById('login-message').innerText = 'Login successful!';
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('recommendations-section').style.display = 'block';
        } else {
            document.getElementById('login-message').innerText = 'Login failed.';
        }
    });
}

function getRecommendations() {
    const bookTitle = document.getElementById('book-title').value;

    fetch('/recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({token, book_title: bookTitle})
    })
    .then(response => response.json())
    .then(data => {
        const list = document.getElementById('recommendations-list');
        list.innerHTML = '';  // Clear previous results

        if (Array.isArray(data)) {
            data.forEach(book => {
                const li = document.createElement('li');
                li.textContent = `${book.title} by ${book.authors} (Score: ${book.score.toFixed(2)})`;
                list.appendChild(li);
            });
        } else {
            list.innerHTML = '<li>No recommendations found.</li>';
        }
    });
}
