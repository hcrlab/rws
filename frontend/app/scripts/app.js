/*
Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at http://polymer.github.io/LICENSE.txt
The complete set of authors may be found at http://polymer.github.io/AUTHORS.txt
The complete set of contributors may be found at http://polymer.github.io/CONTRIBUTORS.txt
Code distributed by Google as part of the polymer project is also
subject to an additional IP rights grant found at http://polymer.github.io/PATENTS.txt
*/

(function(document) {
  'use strict';

  // Grab a reference to our auto-binding template
  // and give it some initial binding values
  // Learn more about auto-binding templates at http://goo.gl/Dx1u2g
  var app = document.querySelector('#app');

  // Sets app default base URL
  app.baseUrl = '/';
  if (window.location.port === '') {  // if production
    app.backend = ''; // Backend is same server as frontend.
    // Uncomment app.baseURL below and
    // set app.baseURL to '/your-pathname/' if running from folder in production
    // app.baseUrl = '/polymer-starter-kit/';
  }

  app.displayInstalledToast = function() {
    // Check to make sure caching is actually enabled—it won't be in the dev environment.
    if (!Polymer.dom(document).querySelector('platinum-sw-cache').disabled) {
      Polymer.dom(document).querySelector('#caching-complete').show();
    }
  };

  // Listen for template bound event to know when bindings
  // have resolved and content has been stamped to the page
  app.addEventListener('dom-change', function() {
  });

  // See https://github.com/Polymer/polymer/issues/1381
  window.addEventListener('WebComponentsReady', function() {
    // imports are loaded and elements have been registered
    app.backend = window.location.protocol + '//' + window.location.hostname + ':5001'; // Development configuration
    app.googleClientId = '1078092352894-a2te9m2ejqurfaap9frrvtg6krjds8pv.apps.googleusercontent.com';
  });

  // Scroll page to top and expand header
  app.scrollPageToTop = function() {
    var rwsApp = app.$$('rws-app');
    if (rwsApp) {
      rwsApp.scrollToTop(true);
    }
  };

  app.closeDrawer = function() {
    var rwsApp = app.$$('rws-app');
    if (rwsApp) {
      rwsApp.closeDrawer();
    }
  };
})(document);
