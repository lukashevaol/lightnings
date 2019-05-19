// Functions to import in server.js to manage requests

// Gets posts from database
const getPosts = (request, response) => {

    const pool = require('./pool');
    pool.query('SELECT * FROM posts', (error, results) => {
        if (error) {
            throw error
    }
    response.status(200).json(results.rows)
    })
}

// Sends html with photo and link
const getOverlay = (request, response) => {

    var src = request.body.posts.photo;
    var link = request.body.posts.link;
    var html_res = '<article><a href="https://www.instagram.com/p/' + link +
        '"><div class="image size-cover_thumb"><img src="' + src + 
        '"></div><figcaption>This post on instagram</figcaption></a></article>'
    response.send({
        success: true,
        html: html_res
});
};

module.exports.getOverlay = getOverlay;
module.exports.getPosts = getPosts;
