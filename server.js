// server.js
const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse JSON
app.use(express.json());

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Route to handle clearing tasks
app.post('/clear', (req, res) => {
    // Implement your logic to clear tasks here
    res.status(200).send({ message: 'All tasks and completed tasks have been cleared.' });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});