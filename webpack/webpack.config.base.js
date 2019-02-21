const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");


module.exports = (env = {}) => {
    const devMode = !env.production;

    return {
        context: __dirname,

        entry: [
            'babel-polyfill',
            'classlist-polyfill',
            // entry point of our app. index.js should require other js modules and dependencies it needs
            '../src/xr_web/static/js/index'
        ],

        output: {
            filename: "[name]-[hash].js",
            path: path.resolve(path.join(__dirname, 'static', 'dist')),
            publicPath: "/static/dist/"
        },

        plugins: [ // add all common plugins here
        ],

        module: {
            rules: [ // add all common loaders here
                {
                    test: /\.woff2?(\?v=\d+\.\d+\.\d+)?$/,
                    loader: "url-loader?limit=10000&mimetype=application/font-woff"
                },
                {
                    test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
                    loader: "url-loader?limit=10000&mimetype=application/octet-stream"
                },
                {
                    test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
                    loader: "url-loader?limit=10000&mimetype=application/vnd.ms-fontobject"
                },
                {
                    test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                    loader: "url-loader?limit=10000&mimetype=image/svg+xml"
                },
                {
                    test: /\.png(\?v=\d+\.\d+\.\d+)?$/,
                    loader: "url-loader?limit=10000&mimetype=image/png"
                },
                {
                    test: /\.jpe?g(\?v=\d+\.\d+\.\d+)?$/,
                    loader: "url-loader?limit=10000&mimetype=image/jpeg"
                },
                {
                    test: /\.gif(\?v=\d+\.\d+\.\d+)?$/,
                    loader: "url-loader?limit=10000&mimetype=image/gif"
                },
                {
                    test: /\.jsx?$/,
                    // exclude: /node_modules/,
                    include: [
                        path.resolve(__dirname, "..", "src"), // white-list your app source files
                    ],
                    use: {
                        loader: 'babel-loader'
                    }
                },
                {
                    test: /\.(s?css)$/,
                    use: [
                        devMode ? 'style-loader' : MiniCssExtractPlugin.loader,
                        { loader: 'css-loader', options: { importLoaders: 2 }},
                        { loader: 'postcss-loader', options: {
                            plugins: devMode ? [] : [require('autoprefixer')]
                        }},
                        { loader: 'sass-loader' }
                    ]
                }
            ]
        },
        resolve: {
            modules: ['node_modules'],
            extensions: ['.js', '.jsx']
        }
    };
};
