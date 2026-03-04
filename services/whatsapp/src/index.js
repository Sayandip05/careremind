const express = require('express');
const app = express();

app.use(express.json());

app.post('/send', async (req, res) => {
    res.json({ status: 'sent' });
});

app.listen(3001, () => {
    console.log('WhatsApp service running on port 3001');
});

module.exports = app;
