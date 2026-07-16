import { fetchMe, getToken } from "./auth.js";
import { renderLogin } from "./login.js";
import { initCostingApp } from "./costing/app.js";

async function bootstrap() {
  if (!getToken()) {
    renderLogin(bootstrap);
    return;
  }
  try {
    await fetchMe();
    initCostingApp();
  } catch {
    renderLogin(bootstrap);
  }
}

bootstrap();
