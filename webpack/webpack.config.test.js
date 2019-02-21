const merge = require('webpack-merge');
const common = require('./webpack.config.base.js');


module.exports = (env = {}) => {
    return merge(common(env), {
        mode: "test"
    });
};