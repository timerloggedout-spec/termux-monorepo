// Placeholder service worker
self.addEventListener('install', (_: any) => {
  // @ts-ignore
  self.skipWaiting();
});
self.addEventListener('activate', (_: any) => {
  console.log('SW activated');
});
