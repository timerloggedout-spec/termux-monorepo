/**
 * Browser Sentry init for termux-monorepo web surfaces
 * (commingle-swarm/web, static dashboards, etc.)
 *
 * npm install --save @sentry/browser
 */
import * as Sentry from "@sentry/browser";

Sentry.init({
  dsn: "https://2fbd3c77388239145b6dd872f1e054aa@o4511844213522432.ingest.us.sentry.io/4511844264640512",
  dataCollection: {
    // userInfo: false,
    // httpBodies: [],
  },
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  tracesSampleRate: 1.0,
  tracePropagationTargets: ["localhost", /^https:\/\/yourserver\.io\/api/],
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

// Optional self-test (remove in production):
// Sentry.metrics.count("test_counter", 1);
// myUndefinedFunction();
