module.exports = {
    env: {
        node: true,
        browser: true,
        es6: true,
    },
    extends: ['eslint:recommended', 'prettier'],
    parserOptions: {
        sourceType: 'module',
    },
    rules: {
        'linebreak-style': ['error', 'unix'],
        semi: ['error', 'never'],
    },
}
