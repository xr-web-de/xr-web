const path = require("path");
const merge = require('webpack-merge');
const BundleTracker = require('webpack-bundle-tracker');

const common = require('./webpack.config.base.js');


module.exports = (env = {}) => {
    return merge(common(env), {
        mode: "development",
        devtool: 'source-map',
        output: {
            path: path.resolve('./static/bundles/'),
            publicPath: 'http://localhost:8036/assets/bundles/'
        },
        plugins: [
            new BundleTracker({path: __dirname, filename: './webpack-stats.json'})
        ],
        // webpack-serve serves Hot
        serve: {
            port: 8036,
            // host: '0.0.0.0',
            clipboard: false,
            devMiddleware: {
                publicPath: "/assets/bundles/",
                headers: { "Access-Control-Allow-Origin": "*" }
            }
        }
    });
};