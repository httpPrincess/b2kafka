const webpack = require('webpack');

const config = {
   entry: __dirname +'/src/my.jsx',

   output: {
      path: __dirname+ '/static',
      filename: 'bundle.js',
   },
   resolve: {
      extensions: ['.js', '.jsx']
   },
   module: {
      rules: [
         {
           test: /\.jsx?/,
           exclude: /node_modules/,
           use: 'babel-loader'
         }
      ]
   }

};

module.exports = config;
