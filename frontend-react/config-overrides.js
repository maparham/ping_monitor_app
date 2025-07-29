const webpack = require('webpack');

module.exports = function override(config, env) {
  // Add polyfills for Node.js modules
  config.resolve.fallback = {
    ...config.resolve.fallback,
    "buffer": require.resolve("buffer/"),
    "assert": require.resolve("assert/"),
    "stream": require.resolve("stream-browserify"),
  };

  // Add plugins
  config.plugins.push(
    new webpack.ProvidePlugin({
      Buffer: ['buffer', 'Buffer'],
    })
  );

  return config;
}; 