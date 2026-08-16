// vue.config.js
const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: [
    'quill' // se você estiver usando Quill.js
  ],
  lintOnSave: false,
  chainWebpack: (config) => {
    config.resolve.alias.set('vue$', 'vue/dist/vue.esm-bundler.js')
  }
})