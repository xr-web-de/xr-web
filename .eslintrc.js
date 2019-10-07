module.exports = {
    env: {
        node: true,
        browser: true,
        es6: true,
    },
    extends: ['eslint:recommended', 'prettier'],
    parserOptions: {
        sourceType: 'module',
        ecmaVersion: 8,
    },
    plugins: ['prettier'],
    rules: {},
}
