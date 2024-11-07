let token = null;
const BASE_URL = 'http://127.0.0.1:5001';

// Fonction de connexion
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch(`${BASE_URL}/login`, {  // Utilisation de BASE_URL pour la route de login
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
    })
    .catch(error => console.error('Erreur:', error));
}





// Fonction pour récupérer les recommandations de livres
function getRecommendations() {
    if (!token) {
        alert("Token is missing. Please log in again.");
        return;
    }

    const bookTitle = document.getElementById('book-title').value;

    fetch(`${BASE_URL}/recommendations`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ book_title: bookTitle })
    })
    .then(response => response.json())
    .then(data => {
        const list = document.getElementById('recommendations-list');
        list.innerHTML = '';  // Effacer les résultats précédents

        if (Array.isArray(data)) {
            data.forEach(book => {
                const li = document.createElement('li');
                li.className = "card my-3 p-3";

                // Contenu de l'élément avec vignette cliquable
                li.innerHTML = `
                    <div class="media">
                        <img src="${book.thumbnail}" alt="${book.title} cover" class="mr-3 thumbnail rounded" onclick="showBookDetails(${JSON.stringify(book).replace(/"/g, '&quot;')})">
                        <div class="media-body">
                            <h5 class="mt-0">${book.title}</h5>
                            <p class="text-muted">by ${book.authors}</p>
                            <p>Score: ${book.score.toFixed(2)}</p>
                        </div>
                    </div>
                `;

                // Bouton pour ajouter aux favoris
                const favButton = document.createElement('button');
                favButton.className = "btn btn-outline-success mt-3";
                favButton.textContent = "Add to Favorites";
                favButton.onclick = () => addToFavorites(book);

                li.appendChild(favButton);
                list.appendChild(li);
            });
        } else {
            list.innerHTML = '<li>No recommendations found.</li>';
        }
    })
    .catch(error => {
        console.error("Erreur lors de la requête de recommandations:", error);
        alert("Erreur lors de la requête de recommandations.");
    });
}





// Fonction pour ajouter un livre aux favoris
function addToFavorites(book) {
    if (!token) {
        alert("Token is missing. Please log in again.");
        return;
    }

    console.log("Ajout du livre aux favoris avec le token:", token); // Log pour vérifier le token

    fetch(`${BASE_URL}/favorites`, {  // Utilisation de BASE_URL pour ajouter aux favoris
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,  // Passe le token JWT dans l'en-tête
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            book_title: book.title, 
            book_author: book.authors, // Envoie l'auteur aussi
            book_thumbnail: book.thumbnail  // Inclure la vignette ici
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.msg === "Livre ajouté aux favoris") {
            alert("Book added to favorites!");
        } else {
            alert("Failed to add book to favorites.");
        }
    })
    .catch(error => {
        console.error("Erreur lors de la requête addToFavorites:", error);
        alert("Erreur lors de la requête.");
    });
}


function showFavorites() {
    if (!token) {
        alert("Token is missing. Please log in again.");
        return;
    }

    fetch(`${BASE_URL}/favorites`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const list = document.getElementById('favorites-list');
        list.innerHTML = '';  // Clear previous list

        if (Array.isArray(data) && data.length > 0) {
            data.forEach(book => {
                const li = document.createElement('li');

                // Ajouter l'URL de la vignette directement dans le contenu texte
                li.innerHTML = `<img src="${book.thumbnail}" alt="${book.title} cover" style="width:50px; vertical-align:middle; margin-right:10px;"> 
                                ${book.title} by ${book.author}`;
                
                list.appendChild(li);
            });
        } else {
            list.innerHTML = '<li>No favorites yet.</li>';
        }

        document.getElementById('recommendations-section').style.display = 'none';
        document.getElementById('favorites-section').style.display = 'block';
    })
    .catch(error => {
        console.error("Erreur lors de la récupération des favoris:", error);
        alert("Erreur lors de la récupération des favoris.");
    });
}


// Fonction pour revenir aux recommandations
function showRecommendations() {
    document.getElementById('favorites-section').style.display = 'none';
    document.getElementById('recommendations-section').style.display = 'block';
}




function showBookDetails(book) {
    document.getElementById('book-title').innerText = book.title;
    document.getElementById('book-authors').innerText = `by ${book.authors}`;
    document.getElementById('book-published-year').innerText = `Published Year: ${book.published_year}`;
    document.getElementById('book-average-rating').innerText = `Rating: ${book.average_rating}`;
    document.getElementById('book-categories').innerText = `Categories: ${book.categories}`;
    document.getElementById('book-thumbnail').src = book.thumbnail;
    document.getElementById('book-description').innerText = book.description;

    $('#bookModal').modal('show');
}


// Fonction pour basculer l'affichage de la description dans la modale
function toggleDescription() {
    const descriptionElement = document.getElementById('book-description');
    const toggleButton = document.getElementById('description-toggle');
    if (descriptionElement.style.display === 'none') {
        descriptionElement.style.display = 'block';
        toggleButton.innerText = 'Hide Description';
    } else {
        descriptionElement.style.display = 'none';
        toggleButton.innerText = 'Show Description';
    }
}
