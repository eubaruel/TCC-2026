const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: [],
  lintOnSave: false,
  devServer: {
    port: 8081
  },
  chainWebpack: (config) => {
    config.resolve.alias.set('vue$', 'vue/dist/vue.esm-bundler.js')
  }
})
