/**
 * Application entry point.
 */
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { pinia } from './stores';

// Styles
import './styles/base.css';
import './styles/components.css';

const app = createApp(App);

app.use(pinia);
app.use(router);

app.mount('#app');
