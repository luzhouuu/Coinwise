/**
 * Pinia store configuration.
 */

import { createPinia } from 'pinia';

export const pinia = createPinia();

export * from './transactions';
export * from './sync';
export * from './statistics';
export * from './config';
