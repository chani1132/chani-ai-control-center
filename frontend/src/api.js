import axios from "axios";

const api = axios.create({ baseURL: "/api/v1" });

export const fetchBotStatus = () => api.get("/bot/status").then((r) => r.data);
export const startBot = (payload) => api.post("/bot/start", payload).then((r) => r.data);
export const stopBot = (exchange) => api.post(`/bot/stop/${exchange}`).then((r) => r.data);

export const fetchTrades = (params) => api.get("/trades", { params }).then((r) => r.data);
export const fetchSummary = () => api.get("/trades/summary").then((r) => r.data);

export const fetchUpbitBalance = () => api.get("/exchange/upbit/balance").then((r) => r.data);
export const fetchOkxBalance = () => api.get("/exchange/okx/balance").then((r) => r.data);
export const fetchOkxPositions = () => api.get("/exchange/okx/positions").then((r) => r.data);
export const pingExchanges = () => api.get("/exchange/ping").then((r) => r.data);
