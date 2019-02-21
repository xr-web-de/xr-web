module.exports = {
    "env": {
        "node": true,
        "browser": true,
        "es6": true
    },
    "extends": [
        "eslint:recommended",
    ],
    "parserOptions": {
        "sourceType": "module"
    },
    "rules": {
        "indent": [
            "error",
            4
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "semi": [
            "error",
            "never"
        ]
    }
};
