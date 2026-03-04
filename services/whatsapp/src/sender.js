const axios = require('axios');

async function sendMessage(to, message) {
    const url = `https://graph.facebook.com/v18.0/${process.env.PHONE_NUMBER_ID}/messages`;
    const headers = {
        'Authorization': `Bearer ${process.env.META_WHATSAPP_TOKEN}`,
        'Content-Type': 'application/json'
    };
    const data = {
        messaging_product: 'whatsapp',
        to: to,
        type: 'text',
        text: { body: message }
    };
    return await axios.post(url, data, { headers });
}

module.exports = { sendMessage };
