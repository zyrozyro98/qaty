// ngrok-setup.js
const ngrok = require('ngrok');

const setupNgrok = async (port) => {
    try {
        const url = await ngrok.connect(port);
        console.log(`Public URL: ${url}`);
        return url;
    } catch (error) {
        console.error('Error starting ngrok:', error);
    }
};

module.exports = setupNgrok;
