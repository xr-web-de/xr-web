const path = require('path');
const merge = require('webpack-merge');
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");

const common = require('./webpack.config.base.js');


module.exports = (env = {}) => {
    return merge(common(env), {
        mode: "production",
        output: {
            // set production build path
            path: path.resolve(path.join(__dirname, 'static', 'dist'))
        },
        plugins: [
            new BundleTracker({path: __dirname, filename: 'webpack-stats-production.json'}),

            // builds a seperate main-xyz.css file, so styles can be loaded without js
            new MiniCssExtractPlugin({
                filename: '[name]-[hash].css',
                chunkFilename: '[id]-[hash].css'
            })
        ],
        optimization: {
            minimizer: [
                // minimizes js
                new UglifyJsPlugin(),
                // minimizes css
                new OptimizeCSSAssetsPlugin({})
            ]
        }
    });
};