const templates = {};

function getTemplate(name) {
    return templates[name];
}

function addTemplate(name, template) {
    templates[name] = template;
}

module.exports = { getTemplate, addTemplate };
