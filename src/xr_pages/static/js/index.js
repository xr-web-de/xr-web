/*
 *  index.js
 *  ----------
 *  Entry point for webpack.
 *  Other stuff (styles/js/fonts/components/...) gets included from here.
 */

// import normalize css
import 'normalize.css'

// Import project styles
import '../styles/main.scss'

// import js bootstrapping
import { init } from './init'

init()
