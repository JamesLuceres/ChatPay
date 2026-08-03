// Configuration for your app
// https://v2.quasar.dev/quasar-cli-webpack/quasar-config-file

import { configure } from 'quasar/wrappers'
import path from 'path'
import webpack from 'webpack'

export default configure(function (/* ctx */) {
  return {
    // https://v2.quasar.dev/quasar-cli-webpack/prefetch-feature
    // preFetch: true,

    // app boot file (/src/boot)
    // --> boot files are part of "main.js"
    // https://v2.quasar.dev/quasar-cli-webpack/boot-files
    boot: ['axios'],

    // https://v2.quasar.dev/quasar-cli-webpack/quasar-config-file#css
    css: ['app.scss'],

    // https://github.com/quasarframework/quasar/tree/dev/extras
    extras: [
      // 'ionicons-v4',
      'mdi-v7',
      // 'fontawesome-v6',
      // 'eva-icons',
      // 'themify',
      // 'line-awesome',
      // 'roboto-font-latin-ext', // this or either 'roboto-font', NEVER both!

      'roboto-font', // optional, you are not bound to it
      'material-icons', // optional, you are not bound to it
    ],

    eslint: {
      // fix: true,
      // include: [],
      // exclude: [],
      // cache: false,
      // rawEsbuildEslintOptions: {},
      // rawWebpackEslintPluginOptions: {},
      warnings: true,
      errors: true,
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli-webpack/quasar-config-file#build
    build: {
      vueRouterMode: 'history', // available values: 'hash', 'history'
      // vueRouterBase,
      // vueDevtools,
      // vueOptionsAPI: false,

      // rebuildCache: true, // rebuilds Vite/linter/etc cache on startup

      // publicPath: '/',
      // analyze: true,
      // env: {},
      // rawDefine: {}
      // ignorePublicFolder: true,
      // minify: false,
      // polyfillModulePreload: true,
      // distDir

      esbuildTarget: {
        browser: ['es2022', 'firefox115', 'chrome115', 'safari14'],
        node: 'node20',
      },

      // webpackTranspile
      // webpackTranspileDependencies
      // webpackDevtool

      // htmlFilename
      // rtl
      // showProgress
      // gzip
      // vueCompiler

      extendWebpack(cfg) {
        // Add Node.js polyfills

        cfg.resolve.fallback = {
          ...cfg.resolve.fallback,
          stream: path.resolve(__dirname, 'node_modules/stream-browserify'),
          crypto: path.resolve(__dirname, 'node_modules/crypto-browserify'),
          buffer: path.resolve(__dirname, 'node_modules/buffer'),
          util: path.resolve(__dirname, 'node_modules/util'),
          assert: path.resolve(__dirname, 'node_modules/assert'),
          http: path.resolve(__dirname, 'node_modules/stream-http'),
          https: path.resolve(__dirname, 'node_modules/https-browserify'),
          os: path.resolve(__dirname, 'node_modules/os-browserify/browser'),
          url: path.resolve(__dirname, 'node_modules/url'),
          querystring: path.resolve(__dirname, 'node_modules/querystring-es3'),
          path: path.resolve(__dirname, 'node_modules/path-browserify'),
          fs: false,
          net: false,
          tls: false,
          vm: false, // or: require.resolve('vm-browserify')
        }

        cfg.resolve = cfg.resolve || {}
        cfg.resolve.alias = {
          ...(cfg.resolve.alias || {}),
          'process/browser': path.resolve(__dirname, 'node_modules/process/browser'),
        }

        // Add Buffer to global scope
        cfg.plugins.push(
          new webpack.ProvidePlugin({
            Buffer: ['buffer', 'Buffer'],
            process: 'process/browser',
          }),
        )
      },

      // uglifyOptions
      // scssLoaderOptions
      // sassLoaderOptions
      // stylusLoaderOptions
      // lessLoaderOptions
      // vueLoaderOptions
      // tsLoaderOptions
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli-webpack/quasar-config-file#devserver
    devServer: {
      server: {
        type: 'http',
      },
      // https: true
      open: true, // opens browser window automatically
      proxy: [
        {
          context: ['/api'],
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
        {
          context: ['/ws/rooms'],
          target: 'http://localhost:8000',
          ws: true, // enable WebSocket proxying
          changeOrigin: true,
        },
      ],
    },

    // https://v2.quasar.dev/quasar-cli-webpack/quasar-config-file#framework
    framework: {
      config: [
        'QLayout',
        'QHeader',
        'QDrawer',
        'QPageContainer',
        'QPage',
        'QToolbar',
        'QToolbarTitle',
        'QIcon',
        'QBtn',
        'QList',
        'QItem',
        'QItemSection',
        'QAvatar',
        'QInput',
        'QFooter',
        'QScrollArea',
      ],
      // Quasar plugins
      plugins: ['Notify', 'Dark'],

      // iconSet: 'material-icons', // Quasar icon set
      // lang: 'en-US', // Quasar language pack

      // For special cases outside of where the auto-import strategy can have an impact
      // (like functional components as one of the examples),
      // you can manually specify Quasar components/directives to be available everywhere:
      //
      // components: [],
      // directives: [],
    },

    // animations: 'all', // --- includes all animations
    // https://v2.quasar.dev/options/animations
    animations: [],

    // https://v2.quasar.dev/quasar-cli-webpack/quasar-config-file#sourcefiles
    sourceFiles: {
      indexHtmlTemplate: 'index.html',
    },

    // https://v2.quasar.dev/quasar-cli-webpack/developing-ssr/configuring-ssr
    ssr: {
      prodPort: 3000, // The default port that the production server should use
      // (gets superseded if process.env.PORT is specified at runtime)

      middlewares: [
        'render', // keep this as last one
      ],

      // extendPackageJson (json) {},
      // extendSSRWebserverConf (esbuildConf) {},

      // manualStoreSerialization: true,
      // manualStoreSsrContextInjection: true,
      // manualStoreHydration: true,
      // manualPostHydrationTrigger: true,

      pwa: false,
      // pwaOfflineHtmlFilename: 'offline.html', // do NOT use index.html as name!

      // pwaExtendGenerateSWOptions (cfg) {},
      // pwaExtendInjectManifestOptions (cfg) {}
    },

    // https://v2.quasar.dev/quasar-cli-webpack/developing-pwa/configuring-pwa
    pwa: {
      workboxMode: 'GenerateSW', // 'GenerateSW' or 'InjectManifest'
      // swFilename: 'sw.js',
      // manifestFilename: 'manifest.json',
      // extendManifestJson (json) {},
      // useCredentialsForManifestTag: true,
      // injectPwaMetaTags: false,
      // extendPWACustomSWConf (esbuildConf) {},
      // extendGenerateSWOptions (cfg) {},
      // extendInjectManifestOptions (cfg) {}
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli-webpack/developing-cordova-apps/configuring-cordova
    cordova: {
      // noIosLegacyBuildFlag: true, // uncomment only if you know what you are doing
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli-webpack/developing-capacitor-apps/configuring-capacitor
    capacitor: {
      hideSplashscreen: true,
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli-webpack/developing-electron-apps/configuring-electron
    electron: {
      // extendElectronMainConf (esbuildConf) {},
      // extendElectronPreloadConf (esbuildConf) {},

      // extendPackageJson (json) {},

      // Electron preload scripts (if any) from /src-electron, WITHOUT file extension
      preloadScripts: ['electron-preload'],

      // specify the debugging port to use for the Electron app when running in development mode
      inspectPort: 5858,

      bundler: 'packager', // 'packager' or 'builder'

      packager: {
        // https://github.com/electron-userland/electron-packager/blob/master/docs/api.md#options
        // OS X / Mac App Store
        // appBundleId: '',
        // appCategoryType: '',
        // osxSign: '',
        // protocol: 'myapp://path',
        // Windows only
        // win32metadata: { ... }
      },

      builder: {
        // https://www.electron.build/configuration/configuration

        appId: 'chatpay-frontend',
      },
    },

    // Full list of options: https://v2.quasar.dev/quasar-cli-webpack/developing-browser-extensions/configuring-bex
    bex: {
      // extendBexScriptsConf (esbuildConf) {},
      // extendBexManifestJson (json) {},

      /**
       * The list of extra scripts (js/ts) not in your bex manifest that you want to
       * compile and use in your browser extension. Maybe dynamic use them?
       *
       * Each entry in the list should be a relative filename to /src-bex/
       *
       * @example [ 'my-script.ts', 'sub-folder/my-other-script.js' ]
       */
      extraScripts: [],
    },
  }
})
