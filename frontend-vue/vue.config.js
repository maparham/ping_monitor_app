const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    resolve: {
      fallback: {
        "stream": require.resolve("stream-browserify"),
        "buffer": require.resolve("buffer")
      }
    },
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
        __VUE_PROD_DEVTOOLS__: false,
        __VUE_PROD_TIPS__: false
      })
    ]
  },
  devServer: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    },
    // Disable directory listing to prevent URIError
    static: {
      directory: require('path').join(__dirname, 'public'),
      serveIndex: false
    },
    // Suppress URIError warnings
    onBeforeSetupMiddleware: function (devServer) {
      devServer.app.use((req, res, next) => {
        try {
          decodeURIComponent(req.url)
          next()
        } catch (e) {
          res.status(400).send('Bad Request')
        }
      })
    }
  }
}) 