module.exports = {
  devServer: {
    proxy: {
      '^/ws': {
        ws: true,
        target: 'http://localhost:3000'
      },
      '^/upload': {
        target: 'http://localhost:3000'
      },
    }
  }
}
