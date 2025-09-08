/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './store/templates/**/*.html',   // your app templates
    './loginsys/templates/**/*.html',
    './static/js/**/*.js', 
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/line-clamp'), // optional for truncating descriptions
  ],
}
