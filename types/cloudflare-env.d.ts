// Binding configured in .openai/hosting.json and injected by Sites/Vite.
declare namespace Cloudflare {
  interface Env {
    DB: D1Database;
  }
}
