module.exports = {
    env: {
        node: true,
        browser: true,
        es6: true,
    },
    extends: ['eslint:recommended', 'prettier', 'prettier/babel'],
    parserOptions: {
        sourceType: 'module',
    },
    rules: {},
}
